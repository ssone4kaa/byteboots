from pathlib import Path
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import sys

BASE_DIR = Path(__file__).parent.parent
PLACEHOLDER_PATH = BASE_DIR / "images" / "placeholder.jpg"


def get_placeholder_pixmap(width=None, height=None):
    """Возвращает заглушку для отсутствующего изображения."""
    # Используем resource_path, чтобы работало и в exe
    placeholder_path = resource_path("images/placeholder_2.jpg")
    pixmap = QPixmap(str(placeholder_path))
    if width and height:
        return pixmap.scaled(
            width, height,
            aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio,
            transformMode=Qt.TransformationMode.SmoothTransformation
        )
    return pixmap


def get_base_path() -> Path:
    """Возвращает базовую папку: рядом с exe или корень проекта."""
    if getattr(sys, 'frozen', False):
        # Запущено из собранного exe
        return Path(sys.executable).parent
    else:
        # Запущено из исходников
        return Path(__file__).parent.parent

def resource_path(relative: str) -> Path:
    """Путь к ресурсу, упакованному внутрь exe."""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / relative
    return Path(__file__).parent.parent / relative


def get_scaled_pixmap(image_path: Path, width: int, height: int) -> QPixmap:
    """Масштабирует картинку с заполнением фона, сохраняя пропорции."""
    pixmap = QPixmap(str(image_path))
    
    # Масштабируем с сохранением пропорций, но заполняем весь размер
    scaled = pixmap.scaled(
        width, height,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation
    )
    
    # Обрезаем по центру
    cropped = scaled.copy(
        (scaled.width() - width) // 2,
        (scaled.height() - height) // 2,
        width, height
    )
    
    return cropped