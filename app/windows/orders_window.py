from PyQt6.QtWidgets import (
    QDialog,
    QTableWidgetItem,
    QMessageBox,
    QHeaderView,
    QFileDialog
)
from PyQt6.QtCore import Qt
from PyQt6 import uic

import db
import pandas as pd
from generated.ui_orders_window import Ui_Dialog as Ui_OrdersWindow


class OrdersWindow(QDialog, Ui_OrdersWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self) 

        self.table_orders.setStyleSheet(
            """QTableWidget::item:selected { background-color: #0078d4;}"""
        )
        # Настройка таблицы
        header = self.table_orders.horizontalHeader()
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        # Подключаем кнопки
        self.button_export.clicked.connect(self.export_to_excel)
        self.table_orders.cellDoubleClicked.connect(self.show_order_details)

        self.load_orders()

    def load_orders(self):
        """Загружает список заказов в таблицу."""
        orders = db.get_orders()
        self.table_orders.setRowCount(0)  # Очищаем

        for order in orders:
            row = self.table_orders.rowCount()
            self.table_orders.insertRow(row)

            # ID
            id_item = QTableWidgetItem(str(order["id"]))
            id_item.setData(
                Qt.ItemDataRole.UserRole, order["id"]
            )  # Сохраняем ID для удаления
            self.table_orders.setItem(row, 0, id_item)

            # Дата
            date_item = QTableWidgetItem(order["order_date"])
            self.table_orders.setItem(row, 1, date_item)

            # Клиент
            client_item = QTableWidgetItem(order["client_name"])
            self.table_orders.setItem(row, 2, client_item)

            # Сумма
            total = f"{int(order['total_sum']):,}".replace(",", " ")
            total_item = QTableWidgetItem(f"{total} ₽")
            total_item.setTextAlignment(Qt.AlignmentFlag.AlignRight)
            self.table_orders.setItem(row, 3, total_item)

    def show_order_details(self, row, column):
        order_id = self.table_orders.item(row, 0).data(Qt.ItemDataRole.UserRole)
        client_name = self.table_orders.item(row, 2).text()
        order_date = self.table_orders.item(row, 1).text()

        details = db.get_order_details(order_id)

        html = f"""
        <center>
            <h2 style="font-size: 14pt; font-weight: bold; margin-bottom: 10px;">
                Заказ #{order_id}
            </h2>
            <p style="font-size: 12pt;"><b>Дата:</b> {order_date}</p>
            <p style="font-size: 12pt;"><b>Клиент:</b> {client_name}</p>
            <hr style="border-color: #555">
            <p style="font-size: 14pt; font-weight: bold; margin: 10px 0;">Товары:</p>
        """

        for item in details:
            total = f"{int(item['total']):,}".replace(",", " ")
            html += f"""
            <p style="font-size: 12pt; margin: 5px 0;">
                {item['model_name']} × {item['quantity']} = {total} ₽
            </p>
            """

        total_sum = self.table_orders.item(row, 3).text()
        html += f"""
            <p style="font-size: 14pt; font-weight: bold; margin-top: 10px;">
                Итого: {total_sum}
            </p>
        </center>
        """

        msg = QMessageBox(self)
        msg.setWindowTitle("Детали заказа")
        msg.setText(html)
        msg.exec()

    def export_to_excel(self):
        """Экспортирует заказы в Excel."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить файл Excel",
            "orders_export.xlsx",
            "Excel files (*.xlsx)"
        )
        
        if not file_path:
            return
        
        try:
            # Получаем все заказы
            orders = db.get_orders()
            
            # Преобразуем в DataFrame
            data = []
            for order in orders:
                data.append({
                    'ID': order['id'],
                    'Дата': order['order_date'],
                    'Клиент': order['client_name'],
                    'Сумма': order['total_sum']
                })
            
            df = pd.DataFrame(data)
            
            # Сохраняем в Excel
            df.to_excel(file_path, index=False, engine='openpyxl')
            
            QMessageBox.information(
                self,
                "Экспорт завершён",
                f"Заказы экспортированы в файл:\n{file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Ошибка экспорта",
                f"Не удалось экспортировать заказы:\n{str(e)}"
            )
