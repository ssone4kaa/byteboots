import sqlite3
from pathlib import Path
from contextlib import contextmanager

from datetime import datetime
from app.utils import get_base_path

# Определяем путь к базе относительно этого файла
# Структура: byteboots/db/byteboots.db
# BASE_DIR = Path(__file__).parent
DB_PATH = get_base_path() / "db" / "byteboots.db"


def lower_cyrillic(text):
    """Функция LOWER, работающая с кириллицей."""
    if text is None:
        return None
    return text.lower()


@contextmanager
def get_connection():
    """Контекстный менеджер для безопасной работы с БД."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.create_function("LOWER", 1, lower_cyrillic)
    try:
        yield conn
        conn.commit()  # Автоматический коммит при успешном выходе
    except Exception:
        conn.rollback()  # Откат при ошибке
        raise
    finally:
        conn.close()


def get_filtered_models(
    search_text="",
    season_id=None,
    gender_id=None,
    type_id=None,
    in_stock_only=False,
):

    with get_connection() as conn:
        cur = conn.cursor()
        query = """
            SELECT 
                m.id, m.name, m.price, m.discount, m.quantity, m.image_path,
                c_season.name as season_name, c_season.id as season_id,
                c_gender.name as gender_name, c_gender.id as gender_id,
                c_type.name as type_name, c_type.id as type_id,
                mf.name as manufacturer_name
            FROM models m
            LEFT JOIN categories c_season ON m.season_id = c_season.id
            LEFT JOIN categories c_gender ON m.gender_id = c_gender.id
            LEFT JOIN categories c_type ON m.type_id = c_type.id
            LEFT JOIN manufacturers mf ON m.manufacturer_id = mf.id
            WHERE 1=1
        """
        params = []

        # Поиск по имени или описанию
        if search_text:
            query += """ AND (
                LOWER(m.name) LIKE LOWER(?)
                OR LOWER(m.description) LIKE LOWER(?)
                OR LOWER(c_type.name) LIKE LOWER(?)
            )"""
            search_pattern = f"%{search_text}%"
            params.extend([search_pattern, search_pattern, search_pattern])

        # Фильтр по категориям
        if season_id:
            query += " AND m.season_id = ?"
            params.append(season_id)
        if gender_id:
            query += " AND m.gender_id = ?"
            params.append(gender_id)
        if type_id:
            query += " AND m.type_id = ?"
            params.append(type_id)

        # Только в наличии
        if in_stock_only:
            query += " AND m.quantity > 0"

        cur.execute(query, params)
        return cur.fetchall()


def get_categories_by_type(category_type):
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name FROM categories WHERE category_type = ? ORDER BY name",
            (category_type,),
        )
        return cur.fetchall()


def get_product_by_id(product_id):
    with get_connection() as conn:
        cur = conn.cursor()
        query = """
            SELECT 
                m.id, m.name, m.price, m.discount, m.quantity, m.image_path,
                m.description, m.composition,
                c_season.name as season_name,
                c_gender.name as gender_name,
                c_type.name as type_name,
                mf.name as manufacturer_name
            FROM models m
            LEFT JOIN categories c_season ON m.season_id = c_season.id
            LEFT JOIN categories c_gender ON m.gender_id = c_gender.id
            LEFT JOIN categories c_type ON m.type_id = c_type.id
            LEFT JOIN manufacturers mf ON m.manufacturer_id = mf.id
            WHERE m.id = ?
        """
        cur.execute(query, (product_id,))
        return cur.fetchone()


def save_order(client_name: str, items: list) -> int:
    """
    Сохраняет заказ в БД.

    items — список словарей вида:
    [
        {"model_id": 1, "model_name": "ByteWinter", "quantity": 2, "price_per_unit": 8990.0},
        ...
    ]

    Возвращает id созданного заказа.
    """
    total_sum = sum(item["quantity"] * item["price_per_unit"] for item in items)
    order_date = datetime.now().strftime("%Y.%m.%d %H:%M:%S")

    with get_connection() as conn:
        cur = conn.cursor()

        # Считаем следующий номер вручную
        cur.execute("SELECT MAX(id) FROM orders")
        max_id = cur.fetchone()[0]
        next_id = (max_id or 0) + 1

        cur.execute(
            """INSERT INTO orders (id, client_name, order_date, total_sum)
               VALUES (?, ?, ?, ?)""",
            (next_id, client_name, order_date, total_sum),
        )

        # Добавляем позиции
        for item in items:
            cur.execute(
                """INSERT INTO order_items 
                   (order_id, model_id, model_name, quantity, price_per_unit)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    next_id,
                    item["model_id"],
                    item["model_name"],
                    item["quantity"],
                    item["price_per_unit"],
                ),
            )

        # Уменьшаем количество товара на складе
        for item in items:
            cur.execute(
                "UPDATE models SET quantity = quantity - ? WHERE id = ? AND quantity >= ?",
                (item["quantity"], item["model_id"], item["quantity"]),
            )

        return next_id


def get_orders():
    """Получает список всех заказов."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("""SELECT id, client_name, order_date, total_sum 
               FROM orders 
               ORDER BY order_date DESC""")
        return cur.fetchall()


def get_order_details(order_id):
    """Получает детали конкретного заказа (позиции)."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """SELECT oi.model_name, oi.quantity, oi.price_per_unit,
                      oi.quantity * oi.price_per_unit as total
               FROM order_items oi
               WHERE oi.order_id = ?""",
            (order_id,),
        )
        return cur.fetchall()


def delete_order(order_id):
    """Удаляет заказ и его позиции."""
    with get_connection() as conn:
        cur = conn.cursor()
        # Сначала удаляем позиции
        cur.execute("DELETE FROM order_items WHERE order_id = ?", (order_id,))
        # Потом сам заказ
        cur.execute("DELETE FROM orders WHERE id = ?", (order_id,))


def import_products(products: list[dict]) -> tuple[int, int, list[str]]:
    """
    Импортирует товары в БД.

    products — список словарей с данными товаров.
    Возвращает (добавлено новых, обновлено существующих, список ошибок).
    """
    added = 0
    updated = 0
    errors = []

    with get_connection() as conn:
        cur = conn.cursor()

        for i, product in enumerate(products, start=2):
            try:
                # Проверяем обязательные поля
                required = ["name", "manufacturer", "season", "gender", "type", "price"]
                missing = [f for f in required if not product.get(f)]
                if missing:
                    errors.append(f"Строка {i}: отсутствуют поля {', '.join(missing)}")
                    continue

                # Получаем ID производителя
                cur.execute(
                    "SELECT id FROM manufacturers WHERE name = ?",
                    (product["manufacturer"],),
                )
                manufacturer = cur.fetchone()
                if not manufacturer:
                    cur.execute(
                        "INSERT INTO manufacturers (name) VALUES (?)",
                        (product["manufacturer"],),
                    )
                    manufacturer_id = cur.lastrowid
                else:
                    manufacturer_id = manufacturer["id"]

                # Получаем ID категорий
                def get_category_id(name, category_type):
                    cur.execute(
                        "SELECT id FROM categories WHERE name = ? AND category_type = ?",
                        (name, category_type),
                    )
                    cat = cur.fetchone()
                    if not cat:
                        cur.execute(
                            "INSERT INTO categories (name, category_type) VALUES (?, ?)",
                            (name, category_type),
                        )
                        return cur.lastrowid
                    return cat["id"]

                season_id = get_category_id(product["season"], "season")
                gender_id = get_category_id(product["gender"], "gender")
                type_id = get_category_id(product["type"], "type")

                # Проверяем, существует ли товар с такими же характеристиками
                cur.execute(
                    """
                    SELECT id, quantity FROM models 
                    WHERE name = ? 
                      AND manufacturer_id = ? 
                      AND season_id = ? 
                      AND gender_id = ? 
                      AND type_id = ?
                """,
                    (product["name"], manufacturer_id, season_id, gender_id, type_id),
                )
                existing = cur.fetchone()

                if existing:
                    # Товар существует — обновляем данные и увеличиваем количество
                    new_quantity = existing["quantity"] + int(
                        product.get("quantity", 0)
                    )

                    cur.execute(
                        """
                        UPDATE models SET
                            season_id = ?,
                            gender_id = ?,
                            type_id = ?,
                            price = ?,
                            discount = ?,
                            quantity = ?,
                            composition = ?,
                            description = ?
                        WHERE id = ?
                    """,
                        (
                            season_id,
                            gender_id,
                            type_id,
                            float(product["price"]),
                            int(product.get("discount", 0)),
                            new_quantity,
                            product.get("composition", ""),
                            product.get("description", ""),
                            existing["id"],
                        ),
                    )

                    updated += 1

                else:
                    # Товар не существует — создаём новый
                    cur.execute(
                        """
                        INSERT INTO models 
                        (name, manufacturer_id, season_id, gender_id, type_id, 
                         price, discount, quantity, composition, description)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            product["name"],
                            manufacturer_id,
                            season_id,
                            gender_id,
                            type_id,
                            float(product["price"]),
                            int(product.get("discount", 0)),
                            int(product.get("quantity", 0)),
                            product.get("composition", ""),
                            product.get("description", ""),
                        ),
                    )

                    added += 1

            except Exception as e:
                errors.append(f"Строка {i}: {str(e)}")

        return added, updated, errors
