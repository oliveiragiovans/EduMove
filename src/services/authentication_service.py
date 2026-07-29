"""Authentication workflow for active EduMove teachers."""

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.business_rules.teacher_rules import (
    MAX_PASSWORD_LENGTH,
    TeacherValidationError,
    normalize_teacher_email,
)
from src.models.school import School
from src.models.teacher import Teacher, TeacherRole
from src.security.passwords import (
    hash_password,
    password_needs_rehash,
    verify_password,
)
from src.services.exceptions import AuthenticationError


_DUMMY_PASSWORD_HASH = hash_password(
    "credencial-temporária-para-comparação"
)
_GENERIC_AUTHENTICATION_MESSAGE = "E-mail ou senha inválidos."


@dataclass(frozen=True)
class AuthenticatedTeacher:
    """Minimal identity data safe to retain in a Streamlit session."""

    teacher_id: int
    school_id: int
    name: str
    email: str
    role: TeacherRole


class AuthenticationService:
    """Authenticate teachers without exposing account existence or status."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def authenticate(
        self,
        *,
        email: Any,
        password: Any,
    ) -> AuthenticatedTeacher:
        """Return an active identity when both credentials match."""

        normalized_email = self._normalize_login_email(email)
        password_candidate = self._normalize_login_password(password)
        teacher = self.session.scalar(
            select(Teacher)
            .join(School, Teacher.school_id == School.school_id)
            .where(
                Teacher.email == normalized_email,
                Teacher.is_active.is_(True),
                School.is_active.is_(True),
            )
        )
        comparison_hash = (
            teacher.password_hash
            if teacher is not None
            else _DUMMY_PASSWORD_HASH
        )

        if not verify_password(comparison_hash, password_candidate):
            raise AuthenticationError(_GENERIC_AUTHENTICATION_MESSAGE)

        if teacher is None:
            raise AuthenticationError(_GENERIC_AUTHENTICATION_MESSAGE)

        if password_needs_rehash(teacher.password_hash):
            teacher.password_hash = hash_password(password_candidate)
            self.session.flush()

        return AuthenticatedTeacher(
            teacher_id=teacher.teacher_id,
            school_id=teacher.school_id,
            name=teacher.name,
            email=teacher.email,
            role=teacher.role,
        )

    @staticmethod
    def _normalize_login_email(value: Any) -> str:
        try:
            return normalize_teacher_email(value)
        except TeacherValidationError:
            return "__invalid_email__"

    @staticmethod
    def _normalize_login_password(value: Any) -> str:
        if not isinstance(value, str) or len(value) > MAX_PASSWORD_LENGTH:
            return ""

        return value
