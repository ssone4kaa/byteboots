from PyQt6.QtWidgets import (
    QDialog,
    QListWidgetItem,
    QWidget,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QPushButton,
    QMessageBox,
    QInputDialog,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6 import uic
import db
from app.cart import Cart
from generated.ui_cart_window import Ui_Dialog as Ui_CartWindow


class CartItemWidget(QWidget):
    """Виджет одной позиции корзины."""

    def __init__(self, item, cart, cart_window):

        super().__init__()
        self.item = item
        self.cart = cart
        self.cart_window = cart_window

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # Название товара
        self.label_name = QLabel(item.name)
        self.label_name.setMinimumWidth(200)
        self.label_name.setStyleSheet("font-size: 14pt;")
        layout.addWidget(self.label_name)

        # Цена за единицу
        price_formatted = f"{int(item.price_per_unit):,}".replace(",", " ")
        self.label_price = QLabel(f"{price_formatted} ₽")
        self.label_price.setMinimumWidth(100)
        self.label_price.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_price.setStyleSheet("font-size: 14pt;")
        layout.addWidget(self.label_price)

        # Спинбокс количества
        self.spin_quantity = QSpinBox()
        self.spin_quantity.setMinimum(1)
        self.spin_quantity.setMaximum(item.max_quantity)
        self.spin_quantity.setValue(item.quantity)
        self.spin_quantity.setStyleSheet("""QSpinBox {font-size: 14pt;}""")
        self.spin_quantity.valueChanged.connect(self.on_quantity_changed)
        layout.addWidget(self.spin_quantity)

        # Сумма позиции
        self.label_total = QLabel()
        self.label_total.setMinimumWidth(100)
        self.label_total.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_total.setStyleSheet("font-size: 14pt;")

        self.update_total()
        layout.addWidget(self.label_total)

        # Кнопка удаления
        self.button_remove = QPushButton("✕")
        self.button_remove.setFixedSize(30, 30)
        self.button_remove.clicked.connect(self.on_remove)
        layout.addWidget(self.button_remove)

    def on_quantity_changed(self, quantity):
        """Обработка изменения количества."""
        self.cart.update_quantity(self.item.model_id, quantity)
        self.update_total()
        self.cart_window.update_total()

    def on_remove(self):
        """Удаление товара из корзины."""
        self.cart.remove(self.item.model_id)
        self.cart_window.populate_cart()

    def update_total(self):
        """Обновляет сумму позиции."""
        total = self.item.price_per_unit * self.spin_quantity.value()
        total_formatted = f"{int(total):,}".replace(",", " ")
        self.label_total.setText(f"{total_formatted} ₽")


class CartWindow(QDialog, Ui_CartWindow):
    def __init__(self, cart: Cart, parent=None):
        super().__init__(parent)
        self.cart = cart
        self.order_placed = False
        self.cart_widgets = {}  # model_id -> CartItemWidget

        self.setupUi(self)

        # Подключение кнопки
        self.button_checkout.clicked.connect(self.checkout)

        # Заполняем корзину
        self.populate_cart()

    def populate_cart(self):
        """Заполняет список корзины."""
        self.list_cart.clear()
        self.cart_widgets.clear()

        items = self.cart.get_items()

        if not items:
            self.label_empty.setVisible(True)
            self.list_cart.setVisible(False)
            self.label_total_sum.setText("0 ₽")
            return

        self.label_empty.setVisible(False)
        self.list_cart.setVisible(True)

        for item in items:
            # Создаем widget с правильными callback'ами
            widget = CartItemWidget(
                item, self.cart, self  # Передаем ссылку на окно корзины
            )

            list_item = QListWidgetItem()
            list_item.setSizeHint(QSize(550, 50))
            self.list_cart.addItem(list_item)
            self.list_cart.setItemWidget(list_item, widget)

            self.cart_widgets[item.model_id] = widget

        self.update_total()

    def on_quantity_changed(self, model_id, quantity):
        """Обработка изменения количества."""
        self.cart.update_quantity(model_id, quantity)

        # Обновляем сумму позиции
        if model_id in self.cart_widgets:
            self.cart_widgets[model_id].update_total()

        self.update_total()

    def on_remove(self, model_id):
        """Удаление товара из корзины."""
        self.cart.remove(model_id)
        self.populate_cart()  # Перерисовываем весь список

    def update_total(self):
        """Обновляет итоговую сумму."""
        total = self.cart.get_total()
        total_formatted = f"{int(total):,}".replace(",", " ")
        self.label_total_sum.setText(f"{total_formatted} ₽")

    def checkout(self):
        """Оформление заказа."""
        if self.cart.is_empty():
            QMessageBox.warning(self, "Внимание", "Корзина пуста!")
            return

        # Диалог ввода ФИО клиента
        client_name, ok = QInputDialog.getText(
            self,
            "Оформление заказа",
            "Введите ФИО клиента:",
        )

        if not ok or not client_name.strip():
            return  # Пользователь отменил

        client_name = client_name.strip()

        # Сохраняем заказ
        try:
            items = self.cart.get_items_for_order()
            order_id = db.save_order(client_name, items)
            self.cart.clear()
            self.order_placed = True

            QMessageBox.information(
                self,
                "Заказ оформлен",
                f"Заказ #{order_id} на сумму {self.label_total_sum.text()}\n"
                f"Клиент: {client_name}\n\n"
                f"Остатки на складе обновлены.",
            )

            self.close()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось оформить заказ:\n{e}")
