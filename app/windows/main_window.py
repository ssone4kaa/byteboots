from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow,
    QListWidgetItem,
    QWidget,
    QLabel,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap, QAction
from PyQt6 import uic
from app.windows.orders_window import OrdersWindow
from app.windows.product_detail import ProductDetailWindow
from app.cart import Cart

from generated.ui_main_window import Ui_MainWindow
from generated.ui_product_card import Ui_product_card
import db
import discounts
from app.utils import get_placeholder_pixmap, get_scaled_pixmap
from app.windows.import_window import ImportDialog
from app.utils import get_base_path


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.cart = Cart()

        self.update_cart_counter()

        self.label_empty_catalog = QLabel("Товары не найдены", self.list_catalog)
        self.label_empty_catalog.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_empty_catalog.setStyleSheet("color: gray; font-size: 14pt;")
        self.label_empty_catalog.setVisible(False)
        self.label_empty_catalog.resize(300, 100)

        self.setup_filters()

        # Подключаем сигналы
        self.edit_search.textChanged.connect(self.apply_filters)
        self.combo_season.currentIndexChanged.connect(self.apply_filters)
        self.combo_gender.currentIndexChanged.connect(self.apply_filters)
        self.combo_type.currentIndexChanged.connect(self.apply_filters)
        self.check_in_stock.stateChanged.connect(self.apply_filters)
        self.combo_sort.currentIndexChanged.connect(self.apply_filters)
        self.button_reset_filters.clicked.connect(self.reset_filters)
        self.button_cart.clicked.connect(self.open_cart)
        self.button_orders.clicked.connect(self.open_orders)
        self.button_import.clicked.connect(self.open_import)

        self.apply_filters()


    def update_cart_counter(self):
        """Обновляет текст кнопки 'Корзина (X)'."""
        count = self.cart.get_count()
        self.button_cart.setText(f"Корзина ({count})")

    def open_cart(self):
        from app.windows.cart_window import CartWindow

        dialog = CartWindow(self.cart, parent=self)
        dialog.exec()
        self.update_cart_counter()

        if dialog.order_placed:
            self.apply_filters()

    def open_import(self):
        """Открывает окно импорта товаров."""
        dialog = ImportDialog(parent=self)
        dialog.exec()
        # После импорта обновляем каталог
        self.apply_filters()

    def open_orders(self):
        """Открывает окно списка заказов."""
        dialog = OrdersWindow(parent=self)
        dialog.exec()

    def open_product_detail(self, model_id):
        dialog = ProductDetailWindow(model_id, cart=self.cart, parent=self)
        dialog.exec()
        self.update_cart_counter()

    def setup_filters(self):
        self.combo_season.clear()
        self.combo_season.addItem("Все сезоны", None)
        for row in db.get_categories_by_type("season"):
            self.combo_season.addItem(row["name"], row["id"])

        self.combo_gender.clear()
        self.combo_gender.addItem("Любой пол", None)
        for row in db.get_categories_by_type("gender"):
            self.combo_gender.addItem(row["name"], row["id"])

        self.combo_type.clear()
        self.combo_type.addItem("Все виды", None)
        for row in db.get_categories_by_type("type"):
            self.combo_type.addItem(row["name"], row["id"])

        self.combo_sort.clear()
        self.combo_sort.addItem("По названию", "name")
        self.combo_sort.addItem("Цена ↑", "price_asc")
        self.combo_sort.addItem("Цена ↓", "price_desc")
        self.combo_sort.addItem("По остатку", "quantity")

    def reset_filters(self):
        # Сбрасываем все фильтры на дефолтные значения
        self.edit_search.clear()
        self.combo_season.setCurrentIndex(0)  # "Все сезоны"
        self.combo_gender.setCurrentIndex(0)  # "Любой пол"
        self.combo_type.setCurrentIndex(0)  # "Все виды"
        self.check_in_stock.setChecked(False)
        self.combo_sort.setCurrentIndex(0)

    def apply_filters(self):
        # Блокируем сигналы
        self.edit_search.blockSignals(True)
        self.combo_season.blockSignals(True)
        self.combo_gender.blockSignals(True)
        self.combo_type.blockSignals(True)
        self.check_in_stock.blockSignals(True)
        self.combo_sort.blockSignals(True)

        try:
            # Собираем параметры
            search_text = self.edit_search.text().strip()
            season_id = self.combo_season.currentData()
            gender_id = self.combo_gender.currentData()
            type_id = self.combo_type.currentData()
            in_stock_only = self.check_in_stock.isChecked()
            sort_by = self.combo_sort.currentData()

            # Получаем данные
            products = db.get_filtered_models(
                search_text=search_text,
                season_id=season_id,
                gender_id=gender_id,
                type_id=type_id,
                in_stock_only=in_stock_only,
            )

            # Сортировка
            if sort_by == "price_asc":
                products = sorted(
                    products,
                    key=lambda p: discounts.calculate_final_price(
                        p["price"], p["discount"], current_month=10
                    ),
                )
            elif sort_by == "price_desc":
                products = sorted(
                    products,
                    key=lambda p: discounts.calculate_final_price(
                        p["price"], p["discount"], current_month=10
                    ),
                    reverse=True,
                )
            elif sort_by == "name":
                products = sorted(products, key=lambda p: p["name"])
            elif sort_by == "quantity":
                products = sorted(products, key=lambda p: p["quantity"], reverse=True)

            # Очищаем список
            self.list_catalog.clear()

            IMAGES_DIR = get_base_path() / "images"

            # Создаём карточки
            for product in products:
                # Создаём элемент списка
                item = QListWidgetItem()
                item.setSizeHint(QSize(230, 364))  # Размер ячейки

                # Создаём виджет-карточку
                card_widget = QWidget()
                card = Ui_product_card()
                card.setupUi(card_widget)

                # Заполняем данными
                category_text = (
                    f"{product['type_name']} | {product['manufacturer_name']}"
                )

                final_price = discounts.calculate_final_price(
                    product["price"], product["discount"], current_month=10
                )

                price_formatted = f"{int(product['price']):,}".replace(",", " ")
                final_price_formatted = f"{int(final_price):,}".replace(",", " ")

                if final_price < product["price"]:
                    price_html = f"<s style='color: gray;'>{price_formatted} ₽</s> <b>{final_price_formatted} ₽</b>"
                else:
                    price_html = f"<b>{final_price_formatted} ₽</b>"

                qty = product["quantity"]
                if qty == 0:
                    stock_text, stock_color = "Нет в наличии", "red"
                elif qty <= 3:
                    stock_text, stock_color = "Мало", "orange"
                else:
                    stock_text, stock_color = "Много", "green"

                card.label_name.setText(product["name"])
                card.label_category.setText(category_text)
                card.label_price.setText(price_html)
                card.label_stock.setText(stock_text)
                card.label_stock.setStyleSheet(
                    f"color: {stock_color}; font-weight: bold;"
                )
                image_filename = product["image_path"]
                if image_filename:
                    image_path = IMAGES_DIR / image_filename
                    if image_path.exists():
                        pixmap = get_scaled_pixmap(image_path, 180, 180)
                        card.label_image.setPixmap(pixmap)
                    else:
                        card.label_image.setPixmap(get_placeholder_pixmap(180, 180))
                else:
                    card.label_image.setPixmap(get_placeholder_pixmap(180, 180))

                card.button_open.clicked.connect(
                    lambda checked, pid=product["id"]: self.open_product_detail(pid)
                )

                # Устанавливаем виджет как элемент списка
                self.list_catalog.addItem(item)
                self.list_catalog.setItemWidget(item, card_widget)

            self.label_found.setText(f"Найдено: {len(products)}")
            if len(products) == 0:
                self.label_empty_catalog.setVisible(True)
            else:
                self.label_empty_catalog.setVisible(False)

        finally:
            # Разблокируем сигналы
            self.edit_search.blockSignals(False)
            self.combo_season.blockSignals(False)
            self.combo_gender.blockSignals(False)
            self.combo_type.blockSignals(False)
            self.check_in_stock.blockSignals(False)
            self.combo_sort.blockSignals(False)
