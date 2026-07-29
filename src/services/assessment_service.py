"""Application workflows for assessment management."""

from datetime import date
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.business_rules.assessment_rules import (
    normalize_assessment_changes,
    normalize_assessment_data,
    normalize_assessment_date_range,
    normalize_assessment_id,
    validate_assessment_not_before_birth,
)
from src.models.assessment import Assessment
from src.models.school import School
from src.models.school_class import SchoolClass
from src.models.student import Student
from src.models.teacher import Teacher
from src.services.exceptions import EntityNotFoundError


class AssessmentService:
    """Create, query, update, and deactivate assessments within one school."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def create_assessment(
        self,
        *,
        school_id: int,
        student_id: int,
        teacher_id: int,
        assessment_date: date,
        weight_kg: Any = None,
        height_cm: Any = None,
        notes: Any = None,
    ) -> Assessment:
        """Persist an assessment using the student's current class."""

        self._get_active_school(school_id)
        data = normalize_assessment_data(
            student_id=student_id,
            teacher_id=teacher_id,
            assessment_date=assessment_date,
            weight_kg=weight_kg,
            height_cm=height_cm,
            notes=notes,
        )
        student = self._get_student(
            school_id,
            data["student_id"],
            require_active=True,
            require_active_class=True,
        )
        self._get_teacher(
            school_id,
            data["teacher_id"],
            require_active=True,
        )
        validate_assessment_not_before_birth(
            data["assessment_date"],
            student.birth_date,
        )
        assessment = Assessment(
            class_id=student.class_id,
            **data,
        )
        self.session.add(assessment)
        self.session.flush()
        return assessment

    def get_assessment(
        self,
        school_id: int,
        assessment_id: int,
        *,
        include_inactive: bool = False,
    ) -> Assessment:
        """Return one assessment inside an active school scope."""

        self._get_active_school(school_id)
        statement = (
            select(Assessment)
            .join(
                SchoolClass,
                Assessment.class_id == SchoolClass.class_id,
            )
            .where(
                Assessment.assessment_id == assessment_id,
                SchoolClass.school_id == school_id,
            )
        )

        if not include_inactive:
            statement = statement.where(Assessment.is_active.is_(True))

        assessment = self.session.scalar(statement)

        if assessment is None:
            raise EntityNotFoundError("Avaliação não encontrada.")

        return assessment

    def list_assessments(
        self,
        school_id: int,
        *,
        student_id: int | None = None,
        teacher_id: int | None = None,
        class_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        include_inactive: bool = False,
    ) -> list[Assessment]:
        """Return assessments with optional entity and date filters."""

        self._get_active_school(school_id)
        statement = (
            select(Assessment)
            .join(
                SchoolClass,
                Assessment.class_id == SchoolClass.class_id,
            )
            .where(SchoolClass.school_id == school_id)
        )

        if student_id is not None:
            normalized_student_id = normalize_assessment_id(
                student_id,
                field="student_id",
            )
            self._get_student(
                school_id,
                normalized_student_id,
                require_active=False,
                require_active_class=False,
            )
            statement = statement.where(
                Assessment.student_id == normalized_student_id
            )

        if teacher_id is not None:
            normalized_teacher_id = normalize_assessment_id(
                teacher_id,
                field="teacher_id",
            )
            self._get_teacher(
                school_id,
                normalized_teacher_id,
                require_active=False,
            )
            statement = statement.where(
                Assessment.teacher_id == normalized_teacher_id
            )

        if class_id is not None:
            normalized_class_id = normalize_assessment_id(
                class_id,
                field="class_id",
            )
            self._get_school_class(
                school_id,
                normalized_class_id,
                require_active=False,
            )
            statement = statement.where(
                Assessment.class_id == normalized_class_id
            )

        normalized_from, normalized_to = normalize_assessment_date_range(
            date_from,
            date_to,
        )

        if normalized_from is not None:
            statement = statement.where(
                Assessment.assessment_date >= normalized_from
            )

        if normalized_to is not None:
            statement = statement.where(
                Assessment.assessment_date <= normalized_to
            )

        if not include_inactive:
            statement = statement.where(Assessment.is_active.is_(True))

        statement = statement.order_by(
            Assessment.assessment_date.desc(),
            Assessment.assessment_id.desc(),
        )
        return list(self.session.scalars(statement))

    def update_assessment(
        self,
        school_id: int,
        assessment_id: int,
        **changes: Any,
    ) -> Assessment:
        """Update editable assessment fields without changing its identity."""

        assessment = self.get_assessment(school_id, assessment_id)
        normalized_changes = normalize_assessment_changes(changes)

        if "teacher_id" in normalized_changes:
            self._get_teacher(
                school_id,
                normalized_changes["teacher_id"],
                require_active=True,
            )

        if "assessment_date" in normalized_changes:
            student = self._get_student(
                school_id,
                assessment.student_id,
                require_active=False,
                require_active_class=False,
            )
            validate_assessment_not_before_birth(
                normalized_changes["assessment_date"],
                student.birth_date,
            )

        for field, value in normalized_changes.items():
            setattr(assessment, field, value)

        self.session.flush()
        return assessment

    def deactivate_assessment(
        self,
        school_id: int,
        assessment_id: int,
    ) -> Assessment:
        """Deactivate an assessment without removing its results."""

        assessment = self.get_assessment(school_id, assessment_id)
        assessment.is_active = False
        self.session.flush()
        return assessment

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

    def _get_student(
        self,
        school_id: int,
        student_id: int,
        *,
        require_active: bool,
        require_active_class: bool,
    ) -> Student:
        statement = (
            select(Student)
            .join(SchoolClass, Student.class_id == SchoolClass.class_id)
            .where(
                Student.student_id == student_id,
                SchoolClass.school_id == school_id,
            )
        )

        if require_active:
            statement = statement.where(Student.is_active.is_(True))

        if require_active_class:
            statement = statement.where(SchoolClass.is_active.is_(True))

        student = self.session.scalar(statement)

        if student is None:
            raise EntityNotFoundError(
                "Aluno não encontrado na escola, inativo ou sem turma ativa."
            )

        return student

    def _get_teacher(
        self,
        school_id: int,
        teacher_id: int,
        *,
        require_active: bool,
    ) -> Teacher:
        statement = select(Teacher).where(
            Teacher.teacher_id == teacher_id,
            Teacher.school_id == school_id,
        )

        if require_active:
            statement = statement.where(Teacher.is_active.is_(True))

        teacher = self.session.scalar(statement)

        if teacher is None:
            raise EntityNotFoundError(
                "Professor não encontrado na escola ou inativo."
            )

        return teacher

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
