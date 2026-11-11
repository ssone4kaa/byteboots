-- Производители
INSERT INTO manufacturers (id, name) VALUES
(1, 'ByteSport'),
(2, 'UrbanStep'),
(3, 'ClassicWalk'),
(4, 'TrendyFeet'),
(5, 'ComfortZone');

-- Категории: сезоны
INSERT INTO categories (id, name, category_type) VALUES
(1, 'Летняя обувь', 'season'),
(2, 'Зимняя обувь', 'season'),
(3, 'Демисезонная обувь', 'season');

-- Категории: пол
INSERT INTO categories (id, name, category_type) VALUES
(4, 'Мужская', 'gender'),
(5, 'Женская', 'gender'),
(6, 'Унисекс', 'gender');

-- Категории: вид
INSERT INTO categories (id, name, category_type) VALUES
(7, 'Кроссовки', 'type'),
(8, 'Ботинки', 'type'),
(9, 'Туфли', 'type'),
(10, 'Сандали', 'type'),
(11, 'Сапоги', 'type'),
(12, 'Мокасины', 'type');

-- Модели обуви
-- Покрываем: разные сезоны, полы, виды, цены, скидки, количества, наличие/отсутствие картинок

INSERT INTO models (id, name, manufacturer_id, season_id, gender_id, type_id, composition, description, price, discount, quantity, image_path) VALUES
-- Летняя обувь
(1, 'ByteRunner', 1, 1, 6, 7, 'Текстиль, резина', 'Легкие беговые кроссовки для лета', 5990, 10, 15, 'images/byte_runner.jpg'),
(2, 'SummerBreeze', 4, 1, 5, 10, 'Кожа, пробковая стелька', 'Открытые сандали на каждый день', 3990, 0, 2, 'images/summer_breeze.jpg'),
(3, 'BeachWalk', 2, 1, 6, 10, 'Синтетика, EVA', 'Пляжные шлепанцы', 1990, 25, 8, NULL),

-- Зимняя обувь
(4, 'ByteWinter', 1, 2, 4, 8, 'Натуральная кожа, мех', 'Теплые зимние ботинки с утеплителем', 8990, 0, 5, 'images/byte_winter.jpg'),
(5, 'SnowQueen', 4, 2, 5, 11, 'Замша, натуральный мех', 'Высокие сапоги для снежной погоды', 12990, 15, 3, 'images/snow_queen.jpg'),
(6, 'ArcticPro', 1, 2, 4, 8, 'Мембрана, Thinsulate', 'Профессиональные ботинки для экстремальных температур', 15990, 0, 0, 'images/arctic_pro.jpg'),

-- Демисезонная обувь
(7, 'CityWalker', 2, 3, 6, 8, 'Натуральная кожа', 'Универсальные ботинки на осень/весну', 7490, 10, 12, 'images/city_walker.jpg'),
(8, 'OfficeClassic', 3, 3, 5, 9, 'Кожа, каблук 5 см', 'Элегантные туфли для офиса', 6990, 0, 4, 'images/office_classic.jpg'),
(9, 'CasualMoc', 5, 3, 4, 12, 'Замша, мягкая подошва', 'Удобные мокасины на каждый день', 4990, 20, 7, 'images/casual_moc.jpg'),
(10, 'UrbanSneaker', 2, 3, 6, 7, 'Текстиль, кожа', 'Стильные кроссовки для города', 6490, 0, 20, 'images/urban_sneaker.jpg'),
(11, 'RainShield', 1, 3, 5, 8, 'Водонепроницаемая кожа', 'Ботинки для дождливой погоды', 8490, 15, 6, 'images/rain_shield.jpg'),

-- Дополнительные модели для разнообразия
(12, 'SportElite', 1, 1, 4, 7, 'Сетка, резина', 'Профессиональные беговые кроссовки', 7990, 0, 9, 'images/sport_elite.jpg'),
(13, 'ElegantHeel', 3, 3, 5, 9, 'Лакированная кожа, шпилька 10 см', 'Вечерние туфли', 9990, 30, 1, 'images/elegant_heel.jpg'),
(14, 'WinterBoots', 5, 2, 6, 8, 'Нубук, овчина', 'Утепленные ботинки унисекс', 10990, 10, 11, 'images/winter_boots.jpg'),
(15, 'SummerSandals', 4, 1, 5, 10, 'Кожа, регулируемые ремешки', 'Удобные сандали с анатомической стелькой', 4490, 0, 14, 'images/summer_sandals.jpg');

-- Заказы
INSERT INTO orders (id, client_name, order_date, total_sum) VALUES
(1, 'Иванов Иван Иванович', '2026-10-15 14:30:00', 10782.00),
(2, 'Петрова Мария Сергеевна', '2026-10-18 11:45:00', 12990.00),
(3, 'Сидоров Алексей Петрович', '2026-10-20 16:20:00', 14480.00);

-- Позиции заказов
-- Заказ 1: 2 пары ByteRunner по 5391 руб. (5990 - 10% = 5391)
INSERT INTO order_items (id, order_id, model_id, quantity, price_per_unit) VALUES
(1, 1, 1, 2, 5391.00);

-- Заказ 2: 1 пара SnowQueen по 12990 руб. (без скидки, т.к. зима не в сезоне)
INSERT INTO order_items (id, order_id, model_id, quantity, price_per_unit) VALUES
(2, 2, 5, 1, 12990.00);

-- Заказ 3: 2 пары CityWalker по 6741 руб. (7490 - 10% = 6741)
INSERT INTO order_items (id, order_id, model_id, quantity, price_per_unit) VALUES
(3, 3, 7, 2, 6741.00);