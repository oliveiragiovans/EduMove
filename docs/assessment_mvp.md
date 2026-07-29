# EduMove - Assessment MVP

## Purpose

This document records the initial assessment scope agreed for EduMove version 1.0.
The MVP prioritizes a small set of well-defined assessments that can be applied
consistently and reviewed over time for each student.

Postural observations are educational screening records. They must not be presented
as medical diagnoses.

## Anthropometric Measurements

Each assessment may record:

- body mass in kilograms;
- height in centimeters;
- BMI calculated automatically from body mass and height;
- individual notes from the teacher.

BMI is derived data and should not be stored as an independent source value while it
can be calculated from the historical mass and height measurements.

## Initial Motor Tests

### Adapted Sit-and-Reach

- Protocol: adapted version performed on the floor, without a bench.
- Unit: centimeters.
- Attempts: 2.
- Result: best attempt.
- Result direction: higher is better.
- Precision: one decimal place.
- Pending: confirm and register the source of the reference ranges by age and sex.

### Horizontal Jump

- Unit: centimeters.
- Attempts: 2.
- Result: best attempt.
- Result direction: higher is better.
- The FMS material may support both process criteria and product measurement.

### Single-Leg Balance

- Unit: seconds.
- Attempts: 2.
- Result: best attempt.
- Result direction: higher is better.
- The FMS protocol uses a maximum duration of 30 seconds.

### Ball Reception

- The teacher chooses between 3 and 10 throws according to the assessment context.
- Each throw is recorded individually as a success or failure.
- The final result is displayed as successful receptions over total throws.
- The total number of throws must remain stored with the result so that scores such
  as 3/3 and 3/10 are never interpreted as equivalent.
- The FMS process criteria may be recorded separately from the product result.

## Initial Postural Observations

The MVP includes the following body regions:

- shoulders;
- spine;
- knees;
- feet.

When applicable, observations must be grouped by viewing position so that frontal
and lateral findings are not mixed.

### Implemented Categories

| Region | View | Options |
| --- | --- | --- |
| Shoulders | Frontal | Symmetrical, left elevated, right elevated |
| Shoulders | Lateral | Neutral, protracted |
| Spine | Frontal | No visible asymmetry, simple lateral asymmetry, double lateral asymmetry |
| Spine | Lateral | Neutral, increased thoracic curvature, increased lumbar curvature |
| Knees | Frontal | Neutral, varus appearance, valgus appearance |
| Knees | Lateral | Neutral, semiflexed appearance, hyperextended appearance |
| Feet | Reference view | Neutral arch, flat-arch appearance, high-arch appearance |

Four original and consistent reference boards were created for the application,
avoiding the reuse of images from external documents:

- `assets/posture/shoulders-reference.png`;
- `assets/posture/spine-reference.png`;
- `assets/posture/knees-reference.png`;
- `assets/posture/feet-footprints-reference.png`.

The feet board uses footprints so arch-contact differences remain visible during
the assessment.

## Data Modeling Implications

- `assessments` stores the assessment event, date, anthropometric measurements, and
  general notes.
- `assessment_results` stores attempts and quantitative motor-test results.
- Attempts are submitted as a complete set for one test, allowing fixed protocols
  and the selected 3-to-10 reception throws to be validated before persistence.
- Existing attempt rows are updated or logically deactivated when a set is
  corrected, preserving stable record identities.
- Result summaries use the aggregation method configured in `motor_tests`.
- Binary reception trials are stored as `1` for success and `0` for failure, while
  the interface displays successful receptions over the active attempt count.
- `postural_observation_options` stores the configurable educational catalog,
  including region, view, explanatory text, order, and reference-image path.
- `assessment_postural_observations` stores the choices and optional notes without
  mixing them with numeric `assessment_results`.
- A correction deactivates the previous choice in the same region and view instead
  of deleting it; choices in other views remain independent.
- Reference images should be application assets; the database should store only
  their identifiers or paths and descriptive metadata.
- Protocol names, versions, and sources must be stored so historical results remain
  interpretable if a protocol changes.

## Source Material Reviewed

- `Avaliações Antropométricas e Motoras.pdf`
- `ROTEIRO AVALIAÇÃO.pdf`
- `FMS-Habilidades-Motoras-Fundamentais-Livro-1.pdf`
