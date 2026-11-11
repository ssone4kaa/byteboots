from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6 import uic
from pathlib import Path

import db
import discounts
from app.utils import get_placeholder_pixmap
from app.utils import get_base_path
from generated.ui_product_detail import Ui_product_detail


class ProductDetailWindow(QDialog, Ui_product_detail):
    def __init__(self, model_id, cart, parent=None):
        super().__init__(parent)
        self.setupUi(self) 

        self.model_id = model_id
        self.cart = cart

        # Подключаем кнопку
        self.button_add_to_order.clicked.connect(self.add_to_cart)

        # Загружаем данные
        self.load_product()

    def load_product(self):
        """Загружает данные товара из БД."""
        self.product = db.get_product_by_id(self.model_id)

        if not self.product:
            QMessageBox.warning(self, "Ошибка", "Товар не найден")
            self.close()
            return

        # Заполняем поля
        self.label_name.setText(self.product["name"])
        self.label_category.setText(f"{self.product['manufacturer_name']}")
        self.label_season.setText(f"Сезон: {self.product['season_name']}")
        self.label_gender.setText(f"Пол: {self.product['gender_name']}")

        # Цена со скидкой
        final_price = discounts.calculate_final_price(
            self.product["price"],
            self.product["discount"],
            current_month=10,  # TODO: datetime.now().month
        )

        price_formatted = f"{int(self.product['price']):,}".replace(",", " ")
        final_price_formatted = f"{int(final_price):,}".replace(",", " ")

        if final_price < self.product["price"]:
            price_html = f"<s style='color: gray;'>{price_formatted} ₽</s> <b style='font-size: 14pt;'>{final_price_formatted} ₽</b>"
        else:
            price_html = f"<b style='font-size: 14pt;'>{final_price_formatted} ₽</b>"

        self.label_price.setText(price_html)

        # Описание и состав
        self.label_description.setText(
            self.product["description"] or "Описание отсутствует"
        )

        self.label_composition.setText(
            f"Состав: {self.product["composition"]}" or "Состав не указан"
        )

        # Наличие
        qty = self.product["quantity"]
        self.label_stock.setText(f"В наличии: {qty}")

        # Настраиваем спиннер
        self.spin_quantity.setMinimum(1)
        self.spin_quantity.setMaximum(
            max(1, qty)
        )  # Если 0, то максимум 1 (для отображения)

        # Изображение

        IMAGES_DIR = get_base_path() / "images"
        image_filename = self.product["image_path"]

        if image_filename:
            image_path = IMAGES_DIR / image_filename
            if image_path.exists():
                pixmap = QPixmap(str(image_path))
                self.label_image.setPixmap(
                    pixmap.scaled(
                        300, 300,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                )
            else:
                self.label_image.setPixmap(get_placeholder_pixmap())
        else:
            self.label_image.setPixmap(get_placeholder_pixmap())

        # Блокируем кнопку, если нет в наличии
        if qty == 0:
            self.button_add_to_order.setEnabled(False)
            self.spin_quantity.setEnabled(False)

    def add_to_cart(self):
        """Добавляет товар в корзину."""
        from PyQt6.QtWidgets import QMessageBox

        quantity = self.spin_quantity.value()
        if quantity <= 0:
            return

        # Рассчитываем цену со скидкой
        final_price = discounts.calculate_final_price(
            self.product["price"], self.product["discount"], current_month=10
        )

        # Добавляем в корзину (которую передали через конструктор)
        self.cart.add(
            model_id=self.product["id"],
            name=self.product["name"],
            price_per_unit=final_price,
            quantity=quantity,
            max_quantity=self.product["quantity"],
        )

        # Показываем уведомление
        QMessageBox.information(
            self,
            "Успех",
            f"Товар '{self.product['name']}' добавлен в корзину\nКоличество: {quantity} шт.",
        )

        self.close()
