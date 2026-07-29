"""EduMove domain validation rules."""

from src.business_rules.assessment_rules import (
    AssessmentValidationError,
    normalize_assessment_changes,
    normalize_assessment_data,
)
from src.business_rules.assessment_result_rules import (
    AssessmentResultValidationError,
    aggregate_attempt_values,
    normalize_attempt_notes,
    normalize_attempt_values,
    normalize_result_entity_id,
)
from src.business_rules.school_class_rules import (
    SchoolClassValidationError,
    normalize_school_class_changes,
    normalize_school_class_data,
)
from src.business_rules.postural_observation_rules import (
    PosturalObservationValidationError,
    normalize_postural_entity_id,
    normalize_postural_notes,
    normalize_postural_region,
    normalize_postural_view,
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
    MAX_PASSWORD_LENGTH,
    MIN_PASSWORD_LENGTH,
    TeacherValidationError,
    normalize_new_password,
    normalize_teacher_changes,
    normalize_teacher_data,
)

__all__ = [
    "AssessmentValidationError",
    "AssessmentResultValidationError",
    "PosturalObservationValidationError",
    "SchoolClassValidationError",
    "SchoolValidationError",
    "StudentValidationError",
    "TeacherValidationError",
    "MAX_PASSWORD_LENGTH",
    "MIN_PASSWORD_LENGTH",
    "aggregate_attempt_values",
    "normalize_assessment_changes",
    "normalize_assessment_data",
    "normalize_attempt_notes",
    "normalize_attempt_values",
    "normalize_result_entity_id",
    "normalize_postural_entity_id",
    "normalize_postural_notes",
    "normalize_postural_region",
    "normalize_postural_view",
    "normalize_school_class_changes",
    "normalize_school_class_data",
    "normalize_school_changes",
    "normalize_school_data",
    "normalize_student_changes",
    "normalize_student_data",
    "normalize_teacher_changes",
    "normalize_teacher_data",
    "normalize_new_password",
]
