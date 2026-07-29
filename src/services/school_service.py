"""Application workflows for school management."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.business_rules.school_rules import (
    normalize_school_changes,
    normalize_school_data,
)
from src.models.school import School
from src.services.exceptions import ConflictError, EntityNotFoundError


class SchoolService:
    """Create, query, update, and deactivate schools."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_school(
        self,
        *,
        name: str,
        city: str,
        state: str,
        cnpj: str | None = None,
        email: str | None = None,
        phone: str | None = None,
    ) -> School:
        """Validate and persist a new active school."""

        data = normalize_school_data(
            name=name,
            city=city,
            state=state,
            cnpj=cnpj,
            email=email,
            phone=phone,
        )
        school = School(**data)
        self.session.add(school)
        self._flush_or_raise_conflict()
        return school

    def get_school(
        self,
        school_id: int,
        *,
        include_inactive: bool = False,
    ) -> School:
        """Return one school or raise an expected not-found error."""

        statement = select(School).where(School.school_id == school_id)

        if not include_inactive:
            statement = statement.where(School.is_active.is_(True))

        school = self.session.scalar(statement)

        if school is None:
            raise EntityNotFoundError("Escola não encontrada.")

        return school

    def list_schools(
        self,
        *,
        include_inactive: bool = False,
    ) -> list[School]:
        """Return schools ordered by name and identifier."""

        statement = select(School)

        if not include_inactive:
            statement = statement.where(School.is_active.is_(True))

        statement = statement.order_by(School.name, School.school_id)
        return list(self.session.scalars(statement))

    def update_school(
        self,
        school_id: int,
        **changes: Any,
    ) -> School:
        """Validate and update editable fields of an active school."""

        school = self.get_school(school_id)
        normalized_changes = normalize_school_changes(changes)

        for field, value in normalized_changes.items():
            setattr(school, field, value)

        self._flush_or_raise_conflict()
        return school

    def deactivate_school(self, school_id: int) -> School:
        """Deactivate a school without deleting historical records."""

        school = self.get_school(school_id)
        school.is_active = False
        self.session.flush()
        return school

    def _flush_or_raise_conflict(self) -> None:
        try:
            self.session.flush()
        except IntegrityError as error:
            self.session.rollback()
            raise ConflictError(
                "Já existe uma escola com o CNPJ informado."
            ) from error
