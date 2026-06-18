from workmodels import Training, Exercise

def create_group_workouts():
    groups = {1: [], 2: [], 3: [], 4: []}

    w1_upperA = Training("Верх А (грудь + плечи + трицепс)", is_predefined=True)
    w1_upperA.add_exercise(Exercise("Жим штанги лежа", "", "Грудь", 3, 12))
    w1_upperA.add_exercise(Exercise("Жим гантелей сидя", "", "Дельты", 3, 12))
    w1_upperA.add_exercise(Exercise("Разведение гантелей стоя", "", "Дельты", 3, 15))
    w1_upperA.add_exercise(Exercise("Жим к низу в блочном тренажере", "", "Трицепс", 3, 15))

    w1_upperB = Training("Верх Б (спина + бицепс + трапеция)", is_predefined=True)
    w1_upperB.add_exercise(Exercise("Вертикальная тяга широким хватом", "", "Спина", 3, 12))
    w1_upperB.add_exercise(Exercise("Горизонтальная тяга в блочном тренажере", "", "Спина", 3, 12))
    w1_upperB.add_exercise(Exercise("Подъем штанги на бицепс стоя", "", "Бицепс", 3, 12))
    w1_upperB.add_exercise(Exercise("Шраги со штангой", "", "Трапеции", 3, 15))

    w1_lower = Training("Низ тела + пресс", is_predefined=True)
    w1_lower.add_exercise(Exercise("Приседания со штангой", "", "Ноги", 3, 12))
    w1_lower.add_exercise(Exercise("Жим ногами", "", "Ноги", 3, 15))
    w1_lower.add_exercise(Exercise("Сгибание ног лежа", "", "Ноги", 3, 15))
    w1_lower.add_exercise(Exercise("Подъемы на носки сидя", "", "Икры", 3, 20))
    w1_lower.add_exercise(Exercise("Обратные скручивания", "", "Пресс", 3, 15))

    w1_full = Training("Фулбади", is_predefined=True)
    w1_full.add_exercise(Exercise("Жим ногами", "", "Ноги", 3, 12))
    w1_full.add_exercise(Exercise("Вертикальная тяга широким хватом", "", "Спина", 3, 12))
    w1_full.add_exercise(Exercise("Жим штанги лежа", "", "Грудь", 3, 10))
    w1_full.add_exercise(Exercise("Жим гантелей сидя", "", "Плечи", 3, 12))
    w1_full.add_exercise(Exercise("Подъем штанги на бицепс стоя", "", "Бицепс", 3, 12))
    w1_full.add_exercise(Exercise("Жим к низу в блочном тренажере", "", "Трицепс", 3, 12))
    w1_full.add_exercise(Exercise("Скручивания на скамье с наклоном вниз", "", "Пресс", 3, 15))

    groups[1] = [w1_upperA, w1_upperB, w1_lower, w1_full]


    w2_upperA = Training("Верх А (грудь + плечи + трицепс)", is_predefined=True)
    w2_upperA.add_exercise(Exercise("Жим от груди в тренажере сидя", "", "Грудь", 3, 15))
    w2_upperA.add_exercise(Exercise("Сведения в тренажере Peck-Deck", "", "Грудь", 3, 15))
    w2_upperA.add_exercise(Exercise("Разведение гантелей стоя", "", "Плечи", 3, 15))
    w2_upperA.add_exercise(Exercise("Жим к низу в блочном тренажере", "", "Трицепс", 3, 15))

    w2_upperB = Training("Верх Б (спина + бицепс)", is_predefined=True)
    w2_upperB.add_exercise(Exercise("Горизонтальная тяга в блочном тренажере", "", "Спина", 3, 15))
    w2_upperB.add_exercise(Exercise("Тяга Т-штанги", "", "Спина", 3, 12))   # с опорой коленом на скамью
    w2_upperB.add_exercise(Exercise("Подъем гантелей на бицепс сидя", "", "Бицепс", 3, 15))
    w2_upperB.add_exercise(Exercise("Шраги с гантелями", "", "Трапеции", 3, 15))

    w2_lower = Training("Низ тела (без осевой нагрузки) + пресс", is_predefined=True)
    w2_lower.add_exercise(Exercise("Жим ногами", "", "Ноги", 3, 15))
    w2_lower.add_exercise(Exercise("Приседания в тренажере Смита", "", "Ноги", 3, 12))
    w2_lower.add_exercise(Exercise("Разгибания ног", "", "Ноги", 3, 15))
    w2_lower.add_exercise(Exercise("Сгибание ног лежа", "", "Ноги", 3, 15))
    w2_lower.add_exercise(Exercise("Подъемы на носки сидя", "", "Икры", 3, 20))
    w2_lower.add_exercise(Exercise("Обратные скручивания", "", "Пресс", 3, 12))

    w2_full = Training("Фулбади", is_predefined=True)
    w2_full.add_exercise(Exercise("Жим ногами", "", "Ноги", 3, 12))
    w2_full.add_exercise(Exercise("Горизонтальная тяга в блочном тренажере", "", "Спина", 3, 12))
    w2_full.add_exercise(Exercise("Жим от груди в тренажере сидя", "", "Грудь", 3, 12))
    w2_full.add_exercise(Exercise("Разведение гантелей стоя", "", "Плечи", 3, 15))
    w2_full.add_exercise(Exercise("Подъем гантелей на бицепс сидя", "", "Бицепс", 3, 15))
    w2_full.add_exercise(Exercise("Жим к низу в блочном тренажере", "", "Трицепс", 3, 15))
    w2_full.add_exercise(Exercise("Обратные скручивания", "", "Пресс", 3, 12))

    groups[2] = [w2_upperA, w2_upperB, w2_lower, w2_full]


    w3_upperA = Training("Верх А (грудь+дельты+трицепс)", is_predefined=True)
    w3_upperA.add_exercise(Exercise("Жим штанги лежа", "", "Грудь", 4, 8))
    w3_upperA.add_exercise(Exercise("Жим штанги на скамье с наклоном", "", "Грудь", 3, 10))
    w3_upperA.add_exercise(Exercise("Жим гантелей сидя", "", "Дельты", 4, 10))
    w3_upperA.add_exercise(Exercise("Разведение гантелей стоя", "", "Дельты", 3, 12))
    w3_upperA.add_exercise(Exercise("Жим штанги узким хватом лежа", "", "Трицепс", 3, 10))
    w3_upperA.add_exercise(Exercise("Жим к низу в блочном тренажере", "", "Трицепс", 3, 15))

    w3_upperB = Training("Верх Б (спина+бицепс+трапеция)", is_predefined=True)
    w3_upperB.add_exercise(Exercise("Подтягивания на перекладине", "", "Спина", 4, "макс"))
    w3_upperB.add_exercise(Exercise("Тяга штанги в наклоне", "", "Спина", 4, 10))
    w3_upperB.add_exercise(Exercise("Тяга гантели одной рукой в наклоне", "", "Спина", 3, 12))
    w3_upperB.add_exercise(Exercise("Обратные разведения в тренажере Peck-Deck", "", "Задние дельты", 3, 15))
    w3_upperB.add_exercise(Exercise("Подъем штанги на бицепс стоя", "", "Бицепс", 4, 10))
    w3_upperB.add_exercise(Exercise("Подъемы гантелей на бицепс стоя", "", "Бицепс", 3, 12))
    w3_upperB.add_exercise(Exercise("Шраги со штангой", "", "Трапеции", 3, 12))

    w3_lower = Training("Низ тела + пресс", is_predefined=True)
    w3_lower.add_exercise(Exercise("Приседания со штангой", "", "Ноги", 4, 8))
    w3_lower.add_exercise(Exercise("Гак-приседания", "", "Ноги", 3, 12))
    w3_lower.add_exercise(Exercise("Румынский подъем", "", "Ноги", 4, 10))
    w3_lower.add_exercise(Exercise("Жим ногами", "", "Ноги", 3, 12))
    w3_lower.add_exercise(Exercise("Сгибание ног лежа", "", "Ноги", 3, 12))
    w3_lower.add_exercise(Exercise("Подъемы на носки сидя", "", "Икры", 4, 20))
    w3_lower.add_exercise(Exercise("Подъемы ног в висе", "", "Пресс", 3, 15))
    w3_lower.add_exercise(Exercise("Скручивание на римском стуле", "", "Пресс", 3, 20))

    w3_full = Training("Фулбади", is_predefined=True)
    w3_full.add_exercise(Exercise("Приседания со штангой", "", "Ноги", 3, 8))
    w3_full.add_exercise(Exercise("Жим штанги лежа", "", "Грудь", 3, 8))
    w3_full.add_exercise(Exercise("Тяга штанги в наклоне", "", "Спина", 3, 8))
    w3_full.add_exercise(Exercise("Жим гантелей сидя", "", "Плечи", 3, 10))
    w3_full.add_exercise(Exercise("Румынский подъем", "", "Ноги (задняя поверхность)", 3, 10))
    w3_full.add_exercise(Exercise("Подъем штанги на бицепс стоя", "", "Бицепс", 2, 10))
    w3_full.add_exercise(Exercise("Жим штанги узким хватом лежа", "", "Трицепс", 2, 10))
    w3_full.add_exercise(Exercise("Подъемы ног в висе", "", "Пресс", 3, 12))

    groups[3] = [w3_upperA, w3_upperB, w3_lower, w3_full]


    w4_upperA = Training("Верх А (грудь+плечи+трицепс)", is_predefined=True)
    w4_upperA.add_exercise(Exercise("Жим от груди в тренажере сидя", "", "Грудь", 4, 12))
    w4_upperA.add_exercise(Exercise("Сведения в тренажере Peck-Deck", "", "Грудь", 3, 15))
    w4_upperA.add_exercise(Exercise("Разведение гантелей стоя", "", "Плечи", 3, 15))
    w4_upperA.add_exercise(Exercise("Обратные разведения в тренажере Peck-Deck", "", "Задние дельты", 3, 15))
    w4_upperA.add_exercise(Exercise("Жим к низу в блочном тренажере", "", "Трицепс", 4, 15))

    w4_upperB = Training("Верх Б (спина+бицепс+трапеции)", is_predefined=True)
    w4_upperB.add_exercise(Exercise("Горизонтальная тяга в блочном тренажере", "", "Спина", 4, 12))
    w4_upperB.add_exercise(Exercise("Вертикальная тяга широким хватом", "", "Спина", 4, 12))
    w4_upperB.add_exercise(Exercise("Тяга Т-штанги", "", "Спина", 3, 12))
    w4_upperB.add_exercise(Exercise("Подъем гантелей на бицепс сидя", "", "Бицепс", 3, 12))
    w4_upperB.add_exercise(Exercise("Сгибание рук на бицепс в кроссовере", "", "Бицепс", 3, 15))
    w4_upperB.add_exercise(Exercise("Шраги с гантелями", "", "Трапеции", 3, 15))   # выполняются стоя, но допустимо

    w4_lower = Training("Низ тела + пресс", is_predefined=True)
    w4_lower.add_exercise(Exercise("Жим ногами", "", "Ноги", 4, 12))
    w4_lower.add_exercise(Exercise("Приседания в тренажере Смита", "", "Ноги", 3, 12))
    w4_lower.add_exercise(Exercise("Разгибания ног", "", "Ноги", 3, 15))
    w4_lower.add_exercise(Exercise("Сгибание ног лежа", "", "Ноги", 3, 15))
    w4_lower.add_exercise(Exercise("Подъемы на носки сидя", "", "Икры", 4, 20))
    w4_lower.add_exercise(Exercise("Гиперэкстензия для мышц бедра", "", "Задняя поверхность бедра", 3, 12))
    w4_lower.add_exercise(Exercise("Обратные скручивания", "", "Пресс", 3, 15))

    w4_full = Training("Фулбади", is_predefined=True)
    w4_full.add_exercise(Exercise("Сведения в тренажере Peck-Deck", "", "Грудь", 3, 12))
    w4_full.add_exercise(Exercise("Горизонтальная тяга в блочном тренажере", "", "Спина", 3, 12))
    w4_full.add_exercise(Exercise("Приседания в тренажере Смита", "", "Ноги", 3, 12))
    w4_full.add_exercise(Exercise("Сгибание рук на бицепс в кроссовере", "", "Бицепс", 3, 12))
    w4_full.add_exercise(Exercise("Разгибание руки с гантелью из-за головы", "", "Трицепс", 3, 12))
    w4_full.add_exercise(Exercise("Обратные скручивания", "", "Пресс", 3, 15))
    w4_full.add_exercise(Exercise("Подъемы на носки сидя", "", "Икры", 3, 15))

    groups[4] = [w4_upperA, w4_upperB, w4_lower, w4_full]

    return groups

group_info = {
    1: {"name": "Новичок без проблем ОДА", "tooltip": "Опыт стабильных тренировок до 1 года. Нет травм и заболеваний опорно-двигательного аппарата."},
    2: {"name": "Новичок с проблемами ОДА", "tooltip": "Опыт до 1 года. Есть проблемы: сколиоз, остеохондроз, грыжи, больные колени, артрит и т.д."},
    3: {"name": "Опытный без проблем ОДА", "tooltip": "Опыт стабильных тренировок больше 1 года. Нет проблем с ОДА."},
    4: {"name": "Опытный с проблемами ОДА", "tooltip": "Опыт больше 1 года, но есть заболевания или травмы опорно-двигательного аппарата."}
}