from PyQt6.QtWidgets import (
    QDialog, QFileDialog, QMessageBox, QVBoxLayout,
    QLabel, QPushButton, QProgressBar
)
from PyQt6.QtCore import Qt
import pandas as pd
import db


class ImportDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Импорт товаров из Excel")
        self.setFixedSize(500, 300)
        
        layout = QVBoxLayout(self)
        
        self.label_status = QLabel("Выберите файл Excel для импорта")
        self.label_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_status.setStyleSheet("font-size: 14pt; padding: 20px;")
        layout.addWidget(self.label_status)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.button_select = QPushButton("Выбрать файл")
        self.button_select.setStyleSheet("font-size: 12pt;")
        self.button_select.clicked.connect(self.select_file)
        layout.addWidget(self.button_select)
        
    
    def select_file(self):
        """Открывает диалог выбора файла."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл Excel",
            "",
            "Excel files (*.xlsx *.xls)"
        )
        
        if not file_path:
            return
        
        self.import_products(file_path)
    
    def import_products(self, file_path):
        """Импортирует товары из Excel."""
        try:
            self.button_select.setEnabled(False)
            
            # Читаем Excel
            df = pd.read_excel(file_path)
            
            # Проверяем наличие нужных колонок
            required_columns = ['name', 'manufacturer', 'season', 'gender', 'type', 'price']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"В файле отсутствуют колонки:\n{', '.join(missing_columns)}"
                )
                return
            
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(len(df))
            
            # Преобразуем DataFrame в список словарей
            products = df.to_dict('records')
            
            # Импортируем в БД
            added, updated, errors = db.import_products(products)
            
            # Показываем результат
            result_text = f"Добавлено новых товаров: {added}\n"
            result_text += f"Обновлено существующих: {updated}\n"

            if errors:
                result_text += f"\nОшибок: {len(errors)}\n"
                result_text += "\n".join(errors[:10])
                if len(errors) > 10:
                    result_text += f"\n... и ещё {len(errors) - 10} ошибок"

            QMessageBox.information(self, "Импорт завершён", result_text)         
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка импорта", f"Не удалось импортировать файл:\n{str(e)}")
        
        finally:
            self.button_select.setEnabled(True)
            self.progress_bar.setVisible(False)