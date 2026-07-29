"""EduMove application services."""

from src.services.assessment_service import AssessmentService
from src.services.assessment_result_service import (
    AssessmentResultService,
    AssessmentResultSummary,
)
from src.services.authentication_service import (
    AuthenticatedTeacher,
    AuthenticationService,
)
from src.services.exceptions import (
    AuthenticationError,
    ConflictError,
    EntityNotFoundError,
    ServiceError,
)
from src.services.postural_observation_service import (
    PosturalObservationService,
    PosturalObservationSummary,
)
from src.services.school_service import SchoolService
from src.services.school_class_service import SchoolClassService
from src.services.student_service import StudentService
from src.services.teacher_service import TeacherService

__all__ = [
    "AssessmentService",
    "AssessmentResultService",
    "AssessmentResultSummary",
    "AuthenticatedTeacher",
    "AuthenticationError",
    "AuthenticationService",
    "ConflictError",
    "EntityNotFoundError",
    "PosturalObservationService",
    "PosturalObservationSummary",
    "SchoolService",
    "SchoolClassService",
    "ServiceError",
    "StudentService",
    "TeacherService",
]
