import sys
from PyQt6.QtWidgets import QApplication

# Импорт главного окна
from app.windows.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyleSheet("""QMessageBox,
        QMessageBox QPushButton,
        QInputDialog QLabel {
            font-size: 12pt;
            font-family: 'Segoe UI';}""")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
