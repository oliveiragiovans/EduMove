"""Secure first-school and administrator provisioning workflow."""

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.school import School
from src.models.teacher import Teacher, TeacherRole
from src.services.exceptions import ConflictError
from src.services.school_service import SchoolService
from src.services.teacher_service import TeacherService


@dataclass(frozen=True, slots=True)
class ProvisionedAccess:
    """Identifiers created by the one-time provisioning workflow."""

    school_id: int
    teacher_id: int
    administrator_email: str


class InitialProvisioningService:
    """Create the first school and administrator in one transaction."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def provision(
        self,
        *,
        school_name: str,
        school_city: str,
        school_state: str,
        administrator_name: str,
        administrator_email: str,
        administrator_password: str,
        school_cnpj: str | None = None,
        school_email: str | None = None,
        school_phone: str | None = None,
    ) -> ProvisionedAccess:
        """Provision an empty database and return the new public identifiers."""

        self._ensure_database_is_empty()
        school = SchoolService(self.session).create_school(
            name=school_name,
            city=school_city,
            state=school_state,
            cnpj=school_cnpj,
            email=school_email,
            phone=school_phone,
        )
        administrator = TeacherService(self.session).create_teacher(
            school_id=school.school_id,
            name=administrator_name,
            email=administrator_email,
            password=administrator_password,
            role=TeacherRole.ADMINISTRATOR,
        )

        return ProvisionedAccess(
            school_id=school.school_id,
            teacher_id=administrator.teacher_id,
            administrator_email=administrator.email,
        )

    def find_existing_school_without_access(self) -> School | None:
        """Return the sole active school when no access account exists yet."""

        existing_teacher = self.session.scalar(
            select(Teacher.teacher_id).limit(1)
        )

        if existing_teacher is not None:
            raise ConflictError(
                "O provisionamento inicial não pode ser executado porque "
                "já existe uma conta cadastrada."
            )

        schools = list(
            self.session.scalars(select(School).order_by(School.school_id))
        )

        if not schools:
            return None

        if len(schools) > 1:
            raise ConflictError(
                "Há mais de uma escola cadastrada e nenhuma conta de acesso. "
                "A associação precisa ser resolvida manualmente."
            )

        school = schools[0]
        if not school.is_active:
            raise ConflictError(
                "A única escola cadastrada está inativa. Reative-a antes "
                "do provisionamento."
            )

        return school

    def provision_administrator_for_existing_school(
        self,
        *,
        school_id: int,
        administrator_name: str,
        administrator_email: str,
        administrator_password: str,
    ) -> ProvisionedAccess:
        """Create first access for the sole active school already registered."""

        school = self.find_existing_school_without_access()
        if school is None or school.school_id != school_id:
            raise ConflictError(
                "A escola selecionada não está disponível para o "
                "provisionamento inicial."
            )

        administrator = TeacherService(self.session).create_teacher(
            school_id=school.school_id,
            name=administrator_name,
            email=administrator_email,
            password=administrator_password,
            role=TeacherRole.ADMINISTRATOR,
        )

        return ProvisionedAccess(
            school_id=school.school_id,
            teacher_id=administrator.teacher_id,
            administrator_email=administrator.email,
        )

    def _ensure_database_is_empty(self) -> None:
        existing_school = self.session.scalar(select(School.school_id).limit(1))
        existing_teacher = self.session.scalar(
            select(Teacher.teacher_id).limit(1)
        )

        if existing_school is not None or existing_teacher is not None:
            raise ConflictError(
                "O provisionamento inicial só pode ser executado em um "
                "banco sem escolas e professores."
            )
