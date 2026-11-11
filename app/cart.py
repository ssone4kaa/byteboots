class CartItem:
    """Представляет одну позицию в корзине."""

    def __init__(
        self,
        model_id: int,
        name: str,
        price_per_unit: float,
        quantity: int = 1,
        max_quantity: int = 999,
    ):
        self.model_id = model_id
        self.name = name
        self.price_per_unit = price_per_unit  # Цена на момент добавления (со скидкой)
        self.quantity = quantity
        self.max_quantity = max_quantity

    def get_total(self) -> float:
        """Общая стоимость позиции."""
        return self.price_per_unit * self.quantity


class Cart:
    """Управление корзиной товаров."""

    def __init__(self):
        self._items = {}  # model_id -> CartItem

    def add(
        self,
        model_id: int,
        name: str,
        price_per_unit: float,
        quantity: int = 1,
        max_quantity: int = 999,
    ) -> None:
        """
        Добавить товар в корзину.
        Если товар уже есть — увеличивает количество.
        """

        if model_id in self._items:
            # Товар уже есть — увеличиваем количество
            self._items[model_id].quantity += quantity
        else:
            # Новый товар
            self._items[model_id] = CartItem(
                model_id, name, price_per_unit, quantity, max_quantity
            )

    def remove(self, model_id: int) -> None:
        """Удалить товар из корзины."""
        if model_id in self._items:
            del self._items[model_id]

    def update_quantity(self, model_id: int, quantity: int) -> None:
        """Изменить количество товара."""
        if model_id in self._items:
            self._items[model_id].quantity = quantity

    def get_items(self) -> list[CartItem]:
        """Вернуть список всех позиций."""
        return list(self._items.values())

    def get_item(self, model_id: int) -> CartItem | None:
        """Получить конкретную позицию по ID."""
        return self._items.get(model_id)

    def get_total(self) -> float:
        """Посчитать общую сумму корзины."""
        return sum(item.get_total() for item in self._items.values())

    def get_count(self) -> int:
        """Вернуть общее количество товаров (сумма всех количеств)."""
        return sum(item.quantity for item in self._items.values())

    def get_unique_count(self) -> int:
        """Вернуть количество уникальных позиций."""
        return len(self._items)

    def clear(self) -> None:
        """Очистить корзину."""
        self._items.clear()

    def is_empty(self) -> bool:
        """Проверить, пуста ли корзина."""
        return len(self._items) == 0

    def __len__(self) -> int:
        """Поддержка len(cart)."""
        return self.get_unique_count()

    def __contains__(self, model_id: int) -> bool:
        """Поддержка: if model_id in cart."""
        return model_id in self._items

    def get_items_for_order(self) -> list[dict]:
        """Возвращает позиции в формате для сохранения заказа."""
        return [
            {
                "model_id": item.model_id,
                "model_name": item.name,
                "quantity": item.quantity,
                "price_per_unit": item.price_per_unit,
            }
            for item in self._items.values()
        ]
