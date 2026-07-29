USE edumove;

-- ==========================================
-- Initial motor tests
-- ==========================================

INSERT INTO motor_tests (
    code,
    name,
    unit,
    result_direction,
    result_type,
    aggregation_method,
    default_attempts,
    min_attempts,
    max_attempts,
    protocol_name,
    protocol_version,
    protocol_source,
    protocol_description,
    is_active
)
VALUES
    (
        'ADAPTED_SIT_AND_REACH',
        'Sentar-e-alcançar adaptado',
        'cm',
        'higher',
        'measurement',
        'maximum',
        2,
        2,
        2,
        'Sentar-e-alcançar adaptado sem banco',
        'MVP 1.0',
        NULL,
        'Realizado no chão com fita métrica. Registra-se a melhor de duas tentativas.',
        TRUE
    ),
    (
        'HORIZONTAL_JUMP',
        'Salto horizontal',
        'cm',
        'higher',
        'measurement',
        'maximum',
        2,
        2,
        2,
        'Habilidades Motoras Fundamentais - Livro 1',
        'Livro 1',
        'Fernando Copetti e Nadia Cristina Valentini',
        'Registra-se em centímetros a melhor de duas tentativas.',
        TRUE
    ),
    (
        'SINGLE_LEG_BALANCE',
        'Equilíbrio unipodal',
        's',
        'higher',
        'measurement',
        'maximum',
        2,
        2,
        2,
        'Habilidades Motoras Fundamentais - Livro 1',
        'Livro 1',
        'Fernando Copetti e Nadia Cristina Valentini',
        'Registra-se o melhor tempo de duas tentativas, limitado a 30 segundos.',
        TRUE
    ),
    (
        'BALL_RECEPTION',
        'Recepção de bola',
        'acertos',
        'higher',
        'binary',
        'sum',
        3,
        3,
        10,
        'Roteiro de avaliação escolar',
        'MVP 1.0',
        'Adaptado de Habilidades Motoras Fundamentais - Livro 1',
        'O professor escolhe de 3 a 10 lançamentos e registra cada recepção como acerto ou erro.',
        TRUE
    ),
    (
        'THROWING_ACCURACY',
        'Precisão de arremesso',
        'acertos',
        'higher',
        'measurement',
        'maximum',
        2,
        2,
        2,
        NULL,
        NULL,
        NULL,
        NULL,
        FALSE
    ),
    (
        'AGILITY',
        'Agilidade',
        's',
        'lower',
        'measurement',
        'minimum',
        2,
        2,
        2,
        NULL,
        NULL,
        NULL,
        NULL,
        FALSE
    )
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    unit = VALUES(unit),
    result_direction = VALUES(result_direction),
    result_type = VALUES(result_type),
    aggregation_method = VALUES(aggregation_method),
    default_attempts = VALUES(default_attempts),
    min_attempts = VALUES(min_attempts),
    max_attempts = VALUES(max_attempts),
    protocol_name = VALUES(protocol_name),
    protocol_version = VALUES(protocol_version),
    protocol_source = VALUES(protocol_source),
    protocol_description = VALUES(protocol_description),
    is_active = VALUES(is_active);

-- ==========================================
-- Initial educational postural options
-- ==========================================

INSERT INTO postural_observation_options (
    code,
    region,
    view_position,
    label,
    description,
    reference_image_path,
    sort_order,
    is_active
)
VALUES
    (
        'SHOULDERS_FRONTAL_SYMMETRICAL',
        'shoulders',
        'frontal',
        'Ombros simétricos',
        'Sem assimetria visível na observação frontal.',
        'assets/posture/shoulders-reference.png',
        1,
        TRUE
    ),
    (
        'SHOULDERS_FRONTAL_LEFT_ELEVATED',
        'shoulders',
        'frontal',
        'Ombro esquerdo elevado',
        'Aparência de elevação do ombro esquerdo na observação frontal.',
        'assets/posture/shoulders-reference.png',
        2,
        TRUE
    ),
    (
        'SHOULDERS_FRONTAL_RIGHT_ELEVATED',
        'shoulders',
        'frontal',
        'Ombro direito elevado',
        'Aparência de elevação do ombro direito na observação frontal.',
        'assets/posture/shoulders-reference.png',
        3,
        TRUE
    ),
    (
        'SHOULDERS_LATERAL_NEUTRAL',
        'shoulders',
        'lateral',
        'Posição neutra dos ombros',
        'Sem projeção anterior visível na observação lateral.',
        'assets/posture/shoulders-reference.png',
        1,
        TRUE
    ),
    (
        'SHOULDERS_LATERAL_PROTRACTED',
        'shoulders',
        'lateral',
        'Ombros projetados à frente',
        'Aparência de projeção anterior dos ombros na observação lateral.',
        'assets/posture/shoulders-reference.png',
        2,
        TRUE
    ),
    (
        'SPINE_FRONTAL_NO_VISIBLE_ASYMMETRY',
        'spine',
        'frontal',
        'Sem assimetria visível',
        'Alinhamento sem assimetria lateral visível.',
        'assets/posture/spine-reference.png',
        1,
        TRUE
    ),
    (
        'SPINE_FRONTAL_SIMPLE_LATERAL_ASYMMETRY',
        'spine',
        'frontal',
        'Assimetria lateral simples',
        'Aparência de uma curvatura lateral simples.',
        'assets/posture/spine-reference.png',
        2,
        TRUE
    ),
    (
        'SPINE_FRONTAL_DOUBLE_LATERAL_ASYMMETRY',
        'spine',
        'frontal',
        'Assimetria lateral dupla',
        'Aparência de duas curvaturas laterais.',
        'assets/posture/spine-reference.png',
        3,
        TRUE
    ),
    (
        'SPINE_LATERAL_NEUTRAL',
        'spine',
        'lateral',
        'Perfil neutro da coluna',
        'Sem aumento visível das curvaturas observadas.',
        'assets/posture/spine-reference.png',
        1,
        TRUE
    ),
    (
        'SPINE_LATERAL_INCREASED_THORACIC_CURVATURE',
        'spine',
        'lateral',
        'Curvatura torácica aumentada',
        'Aparência de aumento da curvatura torácica.',
        'assets/posture/spine-reference.png',
        2,
        TRUE
    ),
    (
        'SPINE_LATERAL_INCREASED_LUMBAR_CURVATURE',
        'spine',
        'lateral',
        'Curvatura lombar aumentada',
        'Aparência de aumento da curvatura lombar.',
        'assets/posture/spine-reference.png',
        3,
        TRUE
    ),
    (
        'KNEES_FRONTAL_NEUTRAL',
        'knees',
        'frontal',
        'Alinhamento neutro dos joelhos',
        'Sem desvio visível no alinhamento frontal.',
        'assets/posture/knees-reference.png',
        1,
        TRUE
    ),
    (
        'KNEES_FRONTAL_VARUS_APPEARANCE',
        'knees',
        'frontal',
        'Aparência de joelhos varos',
        'Joelhos mais afastados com tornozelos mais próximos.',
        'assets/posture/knees-reference.png',
        2,
        TRUE
    ),
    (
        'KNEES_FRONTAL_VALGUS_APPEARANCE',
        'knees',
        'frontal',
        'Aparência de joelhos valgos',
        'Joelhos mais próximos com tornozelos mais afastados.',
        'assets/posture/knees-reference.png',
        3,
        TRUE
    ),
    (
        'KNEES_LATERAL_NEUTRAL',
        'knees',
        'lateral',
        'Perfil neutro dos joelhos',
        'Sem flexão ou hiperextensão visível.',
        'assets/posture/knees-reference.png',
        1,
        TRUE
    ),
    (
        'KNEES_LATERAL_SEMIFLEXED_APPEARANCE',
        'knees',
        'lateral',
        'Aparência semiflexionada',
        'Aparência de semiflexão dos joelhos em repouso.',
        'assets/posture/knees-reference.png',
        2,
        TRUE
    ),
    (
        'KNEES_LATERAL_HYPEREXTENDED_APPEARANCE',
        'knees',
        'lateral',
        'Aparência hiperestendida',
        'Aparência de hiperextensão dos joelhos em repouso.',
        'assets/posture/knees-reference.png',
        3,
        TRUE
    ),
    (
        'FEET_REFERENCE_NEUTRAL_ARCH',
        'feet',
        'reference',
        'Pegada com arco neutro',
        'Contato intermediário do mediopé na pegada.',
        'assets/posture/feet-footprints-reference.png',
        1,
        TRUE
    ),
    (
        'FEET_REFERENCE_LOW_ARCH',
        'feet',
        'reference',
        'Pegada com arco rebaixado',
        'Maior contato do mediopé na pegada.',
        'assets/posture/feet-footprints-reference.png',
        2,
        TRUE
    ),
    (
        'FEET_REFERENCE_HIGH_ARCH',
        'feet',
        'reference',
        'Pegada com arco elevado',
        'Menor contato do mediopé na pegada.',
        'assets/posture/feet-footprints-reference.png',
        3,
        TRUE
    )
ON DUPLICATE KEY UPDATE
    region = VALUES(region),
    view_position = VALUES(view_position),
    label = VALUES(label),
    description = VALUES(description),
    reference_image_path = VALUES(reference_image_path),
    sort_order = VALUES(sort_order),
    is_active = VALUES(is_active);
