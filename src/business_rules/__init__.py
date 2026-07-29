"""EduMove domain validation rules."""

from src.business_rules.assessment_rules import (
    AssessmentValidationError,
    normalize_assessment_changes,
    normalize_assessment_data,
)
from src.business_rules.school_class_rules import (
    SchoolClassValidationError,
    normalize_school_class_changes,
    normalize_school_class_data,
)
from src.business_rules.school_rules import (
    SchoolValidationError,
    normalize_school_changes,
    normalize_school_data,
)
from src.business_rules.student_rules import (
    StudentValidationError,
    normalize_student_changes,
    normalize_student_data,
)
from src.business_rules.teacher_rules import (
    TeacherValidationError,
    normalize_teacher_changes,
    normalize_teacher_data,
)

__all__ = [
    "AssessmentValidationError",
    "SchoolClassValidationError",
    "SchoolValidationError",
    "StudentValidationError",
    "TeacherValidationError",
    "normalize_assessment_changes",
    "normalize_assessment_data",
    "normalize_school_class_changes",
    "normalize_school_class_data",
    "normalize_school_changes",
    "normalize_school_data",
    "normalize_student_changes",
    "normalize_student_data",
    "normalize_teacher_changes",
    "normalize_teacher_data",
]
