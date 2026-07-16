USE edumove;

-- ==========================================
-- Initial motor tests
-- ==========================================

INSERT INTO motor_tests (
    code,
    name,
    unit,
    result_direction
)
VALUES
    (
        'HORIZONTAL_JUMP',
        'Salto horizontal',
        'cm',
        'higher'
    ),
    (
        'SINGLE_LEG_BALANCE',
        'Equilíbrio unipodal',
        's',
        'higher'
    ),
    (
        'BALL_RECEPTION',
        'Recepção de bola',
        'acertos',
        'higher'
    ),
    (
        'THROWING_ACCURACY',
        'Precisão de arremesso',
        'acertos',
        'higher'
    ),
    (
        'AGILITY',
        'Agilidade',
        's',
        'lower'
    )
ON DUPLICATE KEY UPDATE
    name = VALUES(name),
    unit = VALUES(unit),
    result_direction = VALUES(result_direction),
    is_active = TRUE;