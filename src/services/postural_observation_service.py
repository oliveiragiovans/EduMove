"""Application workflows for educational postural observations."""

from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.business_rules.postural_observation_rules import (
    normalize_postural_entity_id,
    normalize_postural_notes,
    normalize_postural_region,
    normalize_postural_view,
)
from src.models.assessment import Assessment
from src.models.postural_observation import (
    AssessmentPosturalObservation,
    PosturalObservationOption,
    PosturalRegion,
    PosturalView,
)
from src.models.school import School
from src.models.school_class import SchoolClass
from src.services.exceptions import EntityNotFoundError


@dataclass(frozen=True)
class PosturalObservationSummary:
    """Display-ready information for one selected posture option."""

    postural_observation_id: int
    assessment_id: int
    postural_option_id: int
    code: str
    region: PosturalRegion
    view_position: PosturalView
    label: str
    description: str | None
    reference_image_path: str | None
    notes: str | None


class PosturalObservationService:
    """Manage posture choices while preserving assessment history."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_options(
        self,
        *,
        region: Any = None,
        view_position: Any = None,
        include_inactive: bool = False,
    ) -> list[PosturalObservationOption]:
        """Return catalog options ordered for the future interface."""

        normalized_region = normalize_postural_region(region)
        normalized_view = normalize_postural_view(view_position)
        statement = select(PosturalObservationOption)

        if not include_inactive:
            statement = statement.where(
                PosturalObservationOption.is_active.is_(True)
            )

        if normalized_region is not None:
            statement = statement.where(
                PosturalObservationOption.region == normalized_region
            )

        if normalized_view is not None:
            statement = statement.where(
                PosturalObservationOption.view_position == normalized_view
            )

        statement = statement.order_by(
            PosturalObservationOption.region,
            PosturalObservationOption.view_position,
            PosturalObservationOption.sort_order,
            PosturalObservationOption.postural_option_id,
        )
        return list(self.session.scalars(statement))

    def save_observation(
        self,
        *,
        school_id: int,
        assessment_id: int,
        postural_option_id: int,
        notes: Any = None,
    ) -> AssessmentPosturalObservation:
        """Select one option and replace a conflicting active choice."""

        normalized_school_id = normalize_postural_entity_id(
            school_id,
            field="school_id",
        )
        normalized_assessment_id = normalize_postural_entity_id(
            assessment_id,
            field="assessment_id",
        )
        normalized_option_id = normalize_postural_entity_id(
            postural_option_id,
            field="postural_option_id",
        )
        normalized_notes = normalize_postural_notes(notes)
        self._get_active_school(normalized_school_id)
        self._get_assessment(
            normalized_school_id,
            normalized_assessment_id,
            require_active=True,
        )
        option = self._get_option(normalized_option_id, require_active=True)
        scoped_observations = list(
            self.session.scalars(
                select(AssessmentPosturalObservation)
                .join(
                    PosturalObservationOption,
                    AssessmentPosturalObservation.postural_option_id
                    == PosturalObservationOption.postural_option_id,
                )
                .where(
                    AssessmentPosturalObservation.assessment_id
                    == normalized_assessment_id,
                    PosturalObservationOption.region == option.region,
                    PosturalObservationOption.view_position
                    == option.view_position,
                )
            )
        )
        selected = next(
            (
                observation
                for observation in scoped_observations
                if observation.postural_option_id == normalized_option_id
            ),
            None,
        )

        for observation in scoped_observations:
            observation.is_active = False

        if selected is None:
            selected = AssessmentPosturalObservation(
                assessment_id=normalized_assessment_id,
                postural_option_id=normalized_option_id,
            )
            self.session.add(selected)

        selected.notes = normalized_notes
        selected.is_active = True
        self.session.flush()
        return selected

    def get_assessment_observations(
        self,
        school_id: int,
        assessment_id: int,
        *,
        include_inactive: bool = False,
    ) -> list[AssessmentPosturalObservation]:
        """Return selections, including those from historical assessments."""

        normalized_school_id = normalize_postural_entity_id(
            school_id,
            field="school_id",
        )
        normalized_assessment_id = normalize_postural_entity_id(
            assessment_id,
            field="assessment_id",
        )
        self._get_active_school(normalized_school_id)
        self._get_assessment(
            normalized_school_id,
            normalized_assessment_id,
            require_active=False,
        )
        statement = (
            select(AssessmentPosturalObservation)
            .join(
                PosturalObservationOption,
                AssessmentPosturalObservation.postural_option_id
                == PosturalObservationOption.postural_option_id,
            )
            .where(
                AssessmentPosturalObservation.assessment_id
                == normalized_assessment_id
            )
        )

        if not include_inactive:
            statement = statement.where(
                AssessmentPosturalObservation.is_active.is_(True)
            )

        statement = statement.order_by(
            PosturalObservationOption.region,
            PosturalObservationOption.view_position,
            PosturalObservationOption.sort_order,
        )
        return list(self.session.scalars(statement))

    def list_observation_summaries(
        self,
        school_id: int,
        assessment_id: int,
    ) -> list[PosturalObservationSummary]:
        """Return active selections together with their reference images."""

        observations = self.get_assessment_observations(
            school_id,
            assessment_id,
        )
        return [
            PosturalObservationSummary(
                postural_observation_id=observation.postural_observation_id,
                assessment_id=observation.assessment_id,
                postural_option_id=observation.postural_option_id,
                code=observation.option.code,
                region=observation.option.region,
                view_position=observation.option.view_position,
                label=observation.option.label,
                description=observation.option.description,
                reference_image_path=observation.option.reference_image_path,
                notes=observation.notes,
            )
            for observation in observations
        ]

    def deactivate_observation(
        self,
        school_id: int,
        assessment_id: int,
        postural_observation_id: int,
    ) -> AssessmentPosturalObservation:
        """Deactivate one selection without deleting its history."""

        normalized_school_id = normalize_postural_entity_id(
            school_id,
            field="school_id",
        )
        normalized_assessment_id = normalize_postural_entity_id(
            assessment_id,
            field="assessment_id",
        )
        normalized_observation_id = normalize_postural_entity_id(
            postural_observation_id,
            field="postural_observation_id",
        )
        self._get_active_school(normalized_school_id)
        self._get_assessment(
            normalized_school_id,
            normalized_assessment_id,
            require_active=True,
        )
        observation = self.session.scalar(
            select(AssessmentPosturalObservation).where(
                AssessmentPosturalObservation.postural_observation_id
                == normalized_observation_id,
                AssessmentPosturalObservation.assessment_id
                == normalized_assessment_id,
                AssessmentPosturalObservation.is_active.is_(True),
            )
        )

        if observation is None:
            raise EntityNotFoundError(
                "Observação postural não encontrada ou inativa."
            )

        observation.is_active = False
        self.session.flush()
        return observation

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

    def _get_assessment(
        self,
        school_id: int,
        assessment_id: int,
        *,
        require_active: bool,
    ) -> Assessment:
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

        if require_active:
            statement = statement.where(Assessment.is_active.is_(True))

        assessment = self.session.scalar(statement)

        if assessment is None:
            raise EntityNotFoundError(
                "Avaliação não encontrada na escola ou inativa."
            )

        return assessment

    def _get_option(
        self,
        postural_option_id: int,
        *,
        require_active: bool,
    ) -> PosturalObservationOption:
        statement = select(PosturalObservationOption).where(
            PosturalObservationOption.postural_option_id
            == postural_option_id
        )

        if require_active:
            statement = statement.where(
                PosturalObservationOption.is_active.is_(True)
            )

        option = self.session.scalar(statement)

        if option is None:
            raise EntityNotFoundError(
                "Opção de observação postural não encontrada ou inativa."
            )

        return option
