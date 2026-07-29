"""Application workflows for teacher management."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.business_rules.teacher_rules import (
    normalize_new_password,
    normalize_teacher_changes,
    normalize_teacher_data,
)
from src.models.school import School
from src.models.teacher import Teacher, TeacherRole
from src.security.passwords import hash_password, verify_password
from src.services.exceptions import (
    AuthenticationError,
    ConflictError,
    EntityNotFoundError,
)


class TeacherService:
    """Create, query, update, and deactivate teachers within one school."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_teacher(
        self,
        *,
        school_id: int,
        name: str,
        email: str,
        password: str,
        role: TeacherRole | str = TeacherRole.TEACHER,
    ) -> Teacher:
        """Validate and persist a teacher for an active school."""

        self._get_active_school(school_id)
        data = normalize_teacher_data(
            name=name,
            email=email,
            role=role,
        )
        password_hash = hash_password(normalize_new_password(password))
        normalized_role = data["role"]

        if normalized_role == TeacherRole.ADMINISTRATOR:
            self._ensure_administrator_available(school_id)

        teacher = Teacher(
            school_id=school_id,
            password_hash=password_hash,
            **data,
        )
        self.session.add(teacher)
        self._flush_or_raise_email_conflict()
        return teacher

    def change_password(
        self,
        school_id: int,
        teacher_id: int,
        *,
        current_password: str,
        new_password: str,
    ) -> Teacher:
        """Replace a password after confirming the current credential."""

        teacher = self.get_teacher(school_id, teacher_id)

        if not verify_password(teacher.password_hash, current_password):
            raise AuthenticationError("Senha atual incorreta.")

        teacher.password_hash = hash_password(
            normalize_new_password(new_password)
        )
        self.session.flush()
        return teacher

    def get_teacher(
        self,
        school_id: int,
        teacher_id: int,
        *,
        include_inactive: bool = False,
    ) -> Teacher:
        """Return one teacher inside a school scope."""

        self._get_active_school(school_id)
        statement = select(Teacher).where(
            Teacher.teacher_id == teacher_id,
            Teacher.school_id == school_id,
        )

        if not include_inactive:
            statement = statement.where(Teacher.is_active.is_(True))

        teacher = self.session.scalar(statement)

        if teacher is None:
            raise EntityNotFoundError("Professor não encontrado.")

        return teacher

    def list_teachers(
        self,
        school_id: int,
        *,
        include_inactive: bool = False,
    ) -> list[Teacher]:
        """Return teachers from one active school ordered by name."""

        self._get_active_school(school_id)
        statement = select(Teacher).where(Teacher.school_id == school_id)

        if not include_inactive:
            statement = statement.where(Teacher.is_active.is_(True))

        statement = statement.order_by(Teacher.name, Teacher.teacher_id)
        return list(self.session.scalars(statement))

    def update_teacher(
        self,
        school_id: int,
        teacher_id: int,
        **changes: Any,
    ) -> Teacher:
        """Validate and update editable fields within the school scope."""

        teacher = self.get_teacher(school_id, teacher_id)
        normalized_changes = normalize_teacher_changes(changes)
        new_role = normalized_changes.get("role")

        if (
            new_role == TeacherRole.ADMINISTRATOR
            and teacher.role != TeacherRole.ADMINISTRATOR
        ):
            self._ensure_administrator_available(
                school_id,
                exclude_teacher_id=teacher_id,
            )

        for field, value in normalized_changes.items():
            setattr(teacher, field, value)

        self._flush_or_raise_email_conflict()
        return teacher

    def deactivate_teacher(
        self,
        school_id: int,
        teacher_id: int,
    ) -> Teacher:
        """Deactivate a teacher without removing historical assessments."""

        teacher = self.get_teacher(school_id, teacher_id)
        teacher.is_active = False
        self.session.flush()
        return teacher

    def _get_active_school(self, school_id: int) -> School:
        school = self.session.scalar(
            select(School).where(
                School.school_id == school_id,
                School.is_active.is_(True),
            )
        )

        if school is None:
            raise EntityNotFoundError("Escola não encontrada ou inativa.")

        return school

    def _ensure_administrator_available(
        self,
        school_id: int,
        *,
        exclude_teacher_id: int | None = None,
    ) -> None:
        statement = select(Teacher.teacher_id).where(
            Teacher.school_id == school_id,
            Teacher.role == TeacherRole.ADMINISTRATOR,
            Teacher.is_active.is_(True),
        )

        if exclude_teacher_id is not None:
            statement = statement.where(
                Teacher.teacher_id != exclude_teacher_id
            )

        if self.session.scalar(statement) is not None:
            raise ConflictError(
                "A escola já possui um administrador ativo."
            )

    def _flush_or_raise_email_conflict(self) -> None:
        try:
            self.session.flush()
        except IntegrityError as error:
            self.session.rollback()
            raise ConflictError(
                "Já existe um professor com o e-mail informado."
            ) from error
