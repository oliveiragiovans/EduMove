"""Application workflows for school-class management."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.business_rules.school_class_rules import (
    normalize_school_class_changes,
    normalize_school_class_data,
)
from src.models.school import School
from src.models.school_class import EducationLevel, SchoolClass, SchoolShift
from src.models.student import Student
from src.models.teacher import Teacher
from src.services.exceptions import ConflictError, EntityNotFoundError


class SchoolClassService:
    """Create, query, update, and deactivate classes within one school."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_school_class(
        self,
        *,
        school_id: int,
        grade_number: int,
        education_level: EducationLevel | str,
        section: str,
        academic_year: int,
        shift: SchoolShift | str,
        teacher_id: int | None = None,
    ) -> SchoolClass:
        """Validate and persist a class for an active school."""

        self._get_active_school(school_id)
        data = normalize_school_class_data(
            teacher_id=teacher_id,
            grade_number=grade_number,
            education_level=education_level,
            section=section,
            academic_year=academic_year,
            shift=shift,
        )
        normalized_teacher_id = data["teacher_id"]

        if normalized_teacher_id is not None:
            self._get_active_teacher(
                school_id,
                normalized_teacher_id,
            )

        school_class = SchoolClass(school_id=school_id, **data)
        self.session.add(school_class)
        self._flush_or_raise_duplicate()
        return school_class

    def get_school_class(
        self,
        school_id: int,
        class_id: int,
        *,
        include_inactive: bool = False,
    ) -> SchoolClass:
        """Return one class inside an active school scope."""

        self._get_active_school(school_id)
        statement = select(SchoolClass).where(
            SchoolClass.class_id == class_id,
            SchoolClass.school_id == school_id,
        )

        if not include_inactive:
            statement = statement.where(SchoolClass.is_active.is_(True))

        school_class = self.session.scalar(statement)

        if school_class is None:
            raise EntityNotFoundError("Turma não encontrada.")

        return school_class

    def list_school_classes(
        self,
        school_id: int,
        *,
        include_inactive: bool = False,
    ) -> list[SchoolClass]:
        """Return classes from one active school in academic order."""

        self._get_active_school(school_id)
        statement = select(SchoolClass).where(
            SchoolClass.school_id == school_id
        )

        if not include_inactive:
            statement = statement.where(SchoolClass.is_active.is_(True))

        statement = statement.order_by(
            SchoolClass.academic_year.desc(),
            SchoolClass.grade_number,
            SchoolClass.section,
            SchoolClass.class_id,
        )
        return list(self.session.scalars(statement))

    def update_school_class(
        self,
        school_id: int,
        class_id: int,
        **changes: Any,
    ) -> SchoolClass:
        """Validate and update editable fields within the school scope."""

        school_class = self.get_school_class(school_id, class_id)
        normalized_changes = normalize_school_class_changes(changes)

        if "teacher_id" in normalized_changes:
            teacher_id = normalized_changes["teacher_id"]

            if teacher_id is not None:
                self._get_active_teacher(school_id, teacher_id)

        for field, value in normalized_changes.items():
            setattr(school_class, field, value)

        self._flush_or_raise_duplicate()
        return school_class

    def deactivate_school_class(
        self,
        school_id: int,
        class_id: int,
    ) -> SchoolClass:
        """Deactivate a class without deleting students or assessments."""

        school_class = self.get_school_class(school_id, class_id)
        self._ensure_no_active_students(class_id)
        school_class.is_active = False
        self.session.flush()
        return school_class

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

    def _get_active_teacher(
        self,
        school_id: int,
        teacher_id: int,
    ) -> Teacher:
        teacher = self.session.scalar(
            select(Teacher).where(
                Teacher.teacher_id == teacher_id,
                Teacher.school_id == school_id,
                Teacher.is_active.is_(True),
            )
        )

        if teacher is None:
            raise EntityNotFoundError(
                "Professor responsável não encontrado na escola ou inativo."
            )

        return teacher

    def _ensure_no_active_students(self, class_id: int) -> None:
        active_student_id = self.session.scalar(
            select(Student.student_id).where(
                Student.class_id == class_id,
                Student.is_active.is_(True),
            )
        )

        if active_student_id is not None:
            raise ConflictError(
                "A turma possui alunos ativos. Transfira ou desative os alunos "
                "antes de desativar a turma."
            )

    def _flush_or_raise_duplicate(self) -> None:
        try:
            self.session.flush()
        except IntegrityError as error:
            self.session.rollback()
            raise ConflictError(
                "Já existe uma turma com a mesma escola, série, seção e ano letivo."
            ) from error
