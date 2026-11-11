PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS manufacturers (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS categories (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL,
    category_type TEXT NOT NULL
        CHECK (category_type IN ('season', 'gender', 'type')),
    UNIQUE (category_type, name)
);

CREATE TABLE IF NOT EXISTS models (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT NOT NULL,
    manufacturer_id INTEGER NOT NULL REFERENCES manufacturers(id),
    season_id       INTEGER NOT NULL REFERENCES categories(id),
    gender_id       INTEGER NOT NULL REFERENCES categories(id),
    type_id         INTEGER NOT NULL REFERENCES categories(id),
    composition     TEXT,
    description     TEXT,
    price           REAL NOT NULL CHECK (price >= 0),
    discount        INTEGER NOT NULL DEFAULT 0
                        CHECK (discount BETWEEN 0 AND 100),
    quantity        INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    image_path      TEXT
);

CREATE TABLE IF NOT EXISTS orders (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    client_name TEXT NOT NULL,
    order_date  TEXT NOT NULL,
    total_sum   REAL NOT NULL DEFAULT 0 CHECK (total_sum >= 0)
);

CREATE TABLE IF NOT EXISTS order_items (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id       INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    model_id       INTEGER NOT NULL REFERENCES models(id) ON DELETE RESTRICT,
    quantity       INTEGER NOT NULL CHECK (quantity > 0),
    price_per_unit REAL NOT NULL CHECK (price_per_unit >= 0)
);

CREATE INDEX IF NOT EXISTS idx_models_name ON models(name);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
