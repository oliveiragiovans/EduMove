"""EduMove database models."""

from src.models.assessment import Assessment
from src.models.assessment_result import AssessmentResult
from src.models.base import Base
from src.models.motor_test import (
    AggregationMethod,
    MotorTest,
    ResultDirection,
    ResultType,
)
from src.models.postural_observation import (
    AssessmentPosturalObservation,
    PosturalObservationOption,
    PosturalRegion,
    PosturalView,
)
from src.models.school import School
from src.models.school_class import EducationLevel, SchoolClass, SchoolShift
from src.models.student import Student, StudentSex
from src.models.teacher import Teacher, TeacherRole

__all__ = [
    "Assessment",
    "AssessmentResult",
    "AssessmentPosturalObservation",
    "AggregationMethod",
    "Base",
    "EducationLevel",
    "MotorTest",
    "PosturalObservationOption",
    "PosturalRegion",
    "PosturalView",
    "ResultDirection",
    "ResultType",
    "School",
    "SchoolClass",
    "SchoolShift",
    "Student",
    "StudentSex",
    "Teacher",
    "TeacherRole",
]
