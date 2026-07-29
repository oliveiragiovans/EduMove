"""Application workflows for student management."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.business_rules.student_rules import (
    normalize_class_id,
    normalize_student_changes,
    normalize_student_data,
    normalize_student_search_name,
)
from src.models.school import School
from src.models.school_class import SchoolClass
from src.models.student import Student, StudentSex
from src.services.exceptions import ConflictError, EntityNotFoundError


class StudentService:
    """Create, query, update, and deactivate students within one school."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_student(
        self,
        *,
        school_id: int,
        class_id: int,
        name: str,
        birth_date: Any,
        sex: StudentSex | str,
        registration_number: str | None = None,
    ) -> Student:
        """Validate and persist a student in an active class."""

        self._get_active_school(school_id)
        data = normalize_student_data(
            class_id=class_id,
            registration_number=registration_number,
            name=name,
            birth_date=birth_date,
            sex=sex,
        )
        self._get_school_class(
            school_id,
            data["class_id"],
            require_active=True,
        )
        student = Student(**data)
        self.session.add(student)
        self._flush_or_raise_registration_conflict()
        return student

    def get_student(
        self,
        school_id: int,
        student_id: int,
        *,
        include_inactive: bool = False,
    ) -> Student:
        """Return one student inside an active school scope."""

        self._get_active_school(school_id)
        statement = (
            select(Student)
            .join(SchoolClass, Student.class_id == SchoolClass.class_id)
            .where(
                Student.student_id == student_id,
                SchoolClass.school_id == school_id,
            )
        )

        if not include_inactive:
            statement = statement.where(Student.is_active.is_(True))

        student = self.session.scalar(statement)

        if student is None:
            raise EntityNotFoundError("Aluno não encontrado.")

        return student

    def list_students(
        self,
        school_id: int,
        *,
        class_id: int | None = None,
        name: str | None = None,
        include_inactive: bool = False,
    ) -> list[Student]:
        """Return students from one school with optional class and name filters."""

        self._get_active_school(school_id)
        statement = (
            select(Student)
            .join(SchoolClass, Student.class_id == SchoolClass.class_id)
            .where(SchoolClass.school_id == school_id)
        )

        if class_id is not None:
            normalized_class_id = normalize_class_id(class_id)
            self._get_school_class(
                school_id,
                normalized_class_id,
                require_active=False,
            )
            statement = statement.where(
                Student.class_id == normalized_class_id
            )

        if name is not None:
            normalized_name = normalize_student_search_name(name)
            statement = statement.where(
                Student.name.contains(normalized_name, autoescape=True)
            )

        if not include_inactive:
            statement = statement.where(Student.is_active.is_(True))

        statement = statement.order_by(Student.name, Student.student_id)
        return list(self.session.scalars(statement))

    def update_student(
        self,
        school_id: int,
        student_id: int,
        **changes: Any,
    ) -> Student:
        """Validate and update editable fields within the school scope."""

        student = self.get_student(school_id, student_id)
        normalized_changes = normalize_student_changes(changes)

        if "class_id" in normalized_changes:
            self._get_school_class(
                school_id,
                normalized_changes["class_id"],
                require_active=True,
            )

        for field, value in normalized_changes.items():
            setattr(student, field, value)

        self._flush_or_raise_registration_conflict()
        return student

    def deactivate_student(
        self,
        school_id: int,
        student_id: int,
    ) -> Student:
        """Deactivate a student without removing assessment history."""

        student = self.get_student(school_id, student_id)
        student.is_active = False
        self.session.flush()
        return student

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

    def _get_school_class(
        self,
        school_id: int,
        class_id: int,
        *,
        require_active: bool,
    ) -> SchoolClass:
        statement = select(SchoolClass).where(
            SchoolClass.class_id == class_id,
            SchoolClass.school_id == school_id,
        )

        if require_active:
            statement = statement.where(SchoolClass.is_active.is_(True))

        school_class = self.session.scalar(statement)

        if school_class is None:
            raise EntityNotFoundError(
                "Turma não encontrada na escola ou inativa."
            )

        return school_class

    def _flush_or_raise_registration_conflict(self) -> None:
        try:
            self.session.flush()
        except IntegrityError as error:
            self.session.rollback()
            raise ConflictError(
                "Já existe um aluno com a matrícula informada."
            ) from error
