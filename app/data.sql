INSERT IGNORE INTO countries (name, code, parsing_code)
VALUES ('Німеччина', 'DE', 'D'),
       ('Австрія', 'AT', 'A'),
       ('Бельгія', 'BE', 'B'),
       ('Іспанія', 'ES', 'E'),
       ('Франція', 'FR', 'F'),
       ('Італія', 'IT', 'I'),
       ('Люксембург', 'LU', 'L'),
       ('Нідерланди', 'NL', 'NL');

INSERT IGNORE INTO fuel_types (key_name, label, code)
VALUES ('gasoline', 'Бензин', 'B'),
       ('diesel', 'Дизель', 'D'),
       ('electric', 'Електро', 'E'),
       ('electric/gasoline', 'Електро/Бензин', '2'),
       ('electric/diesel', 'Електро/Дизель', '3'),
       ('lpg', 'Газ', 'L'),
       ('ethanol', 'Етанол', 'M'),
       ('cng', 'CNG/Метан', 'C'),
       ('hydrogen', 'Водень', 'H'),
       ('others', 'Інше', 'O');