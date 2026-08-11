"""Interactive command for the first EduMove administrator."""

from collections.abc import Callable
from dataclasses import dataclass
from getpass import getpass

from sqlalchemy.exc import SQLAlchemyError

from src.business_rules.school_rules import SchoolValidationError
from src.business_rules.teacher_rules import TeacherValidationError
from src.config.database import session_scope
from src.services.exceptions import ConflictError
from src.services.initial_provisioning_service import InitialProvisioningService


@dataclass(frozen=True, slots=True)
class ProvisioningForm:
    """Values collected interactively without persisting the password."""

    school_name: str
    school_city: str
    school_state: str
    school_cnpj: str | None
    school_email: str | None
    school_phone: str | None
    administrator_name: str
    administrator_email: str
    administrator_password: str


@dataclass(frozen=True, slots=True)
class AdministratorForm:
    """First-administrator credentials collected only in process memory."""

    name: str
    email: str
    password: str


def _required_value(
    label: str,
    input_fn: Callable[[str], str],
) -> str:
    while True:
        value = input_fn(f"{label}: ").strip()
        if value:
            return value
        print(f"{label} é obrigatório.")


def _optional_value(
    label: str,
    input_fn: Callable[[str], str],
) -> str | None:
    return input_fn(f"{label} (opcional): ").strip() or None


def collect_form(
    *,
    input_fn: Callable[[str], str] = input,
    password_fn: Callable[[str], str] = getpass,
) -> ProvisioningForm:
    """Collect school and administrator data without echoing the password."""

    school_name = _required_value("Nome da escola", input_fn)
    school_city = _required_value("Cidade", input_fn)
    school_state = _required_value("UF", input_fn)
    school_cnpj = _optional_value("CNPJ", input_fn)
    school_email = _optional_value("E-mail da escola", input_fn)
    school_phone = _optional_value("Telefone da escola", input_fn)
    administrator = collect_administrator_form(
        input_fn=input_fn,
        password_fn=password_fn,
    )

    return ProvisioningForm(
        school_name=school_name,
        school_city=school_city,
        school_state=school_state,
        school_cnpj=school_cnpj,
        school_email=school_email,
        school_phone=school_phone,
        administrator_name=administrator.name,
        administrator_email=administrator.email,
        administrator_password=administrator.password,
    )


def collect_administrator_form(
    *,
    input_fn: Callable[[str], str] = input,
    password_fn: Callable[[str], str] = getpass,
) -> AdministratorForm:
    """Collect the first administrator without echoing the password."""

    administrator_name = _required_value("Nome da administradora", input_fn)
    administrator_email = _required_value(
        "E-mail de acesso da administradora",
        input_fn,
    )
    administrator_password = password_fn("Senha (não será exibida): ")
    password_confirmation = password_fn("Confirme a senha: ")

    if administrator_password != password_confirmation:
        raise TeacherValidationError(
            "password",
            "As senhas informadas não coincidem.",
        )

    return AdministratorForm(
        name=administrator_name,
        email=administrator_email,
        password=administrator_password,
    )


def main() -> int:
    """Run the local, one-time provisioning command."""

    print("\nEduMove — provisionamento inicial seguro\n")

    try:
        with session_scope() as session:
            existing_school = (
                InitialProvisioningService(session)
                .find_existing_school_without_access()
            )

        if existing_school is None:
            form = collect_form()
            confirmation_message = (
                "\nCriar a primeira escola e administradora? [s/N]: "
            )
        else:
            print(
                "Uma escola ativa sem conta de acesso foi encontrada: "
                f"{existing_school.name} (ID {existing_school.school_id}).\n"
            )
            administrator_form = collect_administrator_form()
            confirmation_message = (
                "\nCriar a primeira administradora para esta escola? [s/N]: "
            )

        confirmation = input(confirmation_message).strip().casefold()

        if confirmation not in {"s", "sim"}:
            print("Provisionamento cancelado. Nenhuma alteração foi realizada.")
            return 0

        with session_scope() as session:
            service = InitialProvisioningService(session)
            if existing_school is None:
                access = service.provision(
                    school_name=form.school_name,
                    school_city=form.school_city,
                    school_state=form.school_state,
                    school_cnpj=form.school_cnpj,
                    school_email=form.school_email,
                    school_phone=form.school_phone,
                    administrator_name=form.administrator_name,
                    administrator_email=form.administrator_email,
                    administrator_password=form.administrator_password,
                )
            else:
                access = service.provision_administrator_for_existing_school(
                    school_id=existing_school.school_id,
                    administrator_name=administrator_form.name,
                    administrator_email=administrator_form.email,
                    administrator_password=administrator_form.password,
                )
    except (SchoolValidationError, TeacherValidationError, ConflictError) as error:
        print(f"\nNão foi possível provisionar o EduMove: {error}")
        return 1
    except SQLAlchemyError:
        print(
            "\nNão foi possível acessar o banco de dados. "
            "Confira a configuração e tente novamente."
        )
        return 1

    print("\nProvisionamento concluído com segurança.")
    print(f"Escola vinculada com identificador {access.school_id}.")
    print(f"Administradora: {access.administrator_email}")
    print("A senha não foi exibida nem armazenada em texto simples.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
