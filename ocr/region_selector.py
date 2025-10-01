import os
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QColor
import mss
from PIL import Image
from .precise_ocr import PreciseOCR

class RegionSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.start = None
        self.end = None
        self.region = {}

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.showFullScreen()

    def mousePressEvent(self, event):
        self.start = event.pos()
        self.end = self.start

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        rect = QRect(self.start, self.end).normalized()
        self.region = {
            "left": rect.x(),
            "top": rect.y(),
            "width": rect.width(),
            "height": rect.height(),
        }
        print("[LOG] Новая область для OCR:", self.region)
        self.close()

    def paintEvent(self, event):
        if self.start and self.end:
            painter = QPainter(self)
            pen = QPen(QColor("#00c9c3"), 2)
            painter.setPen(pen)
            painter.drawRect(QRect(self.start, self.end))


class OCRRegion:
    def __init__(self):
        self.region = {}
        self.ocr_model = PreciseOCR()
        print("[LOG] OCRRegion инициализирован. Старые регионы игнорируются.")

    def select_region(self):
        print("[LOG] Запуск выбора нового региона")
        selector = RegionSelector()
        selector.show()

        while selector.isVisible():
            QApplication.processEvents()

        self.region = selector.region
        print("[LOG] Регион выбран:", self.region)

        if self.region:
            with mss.mss() as sct:
                sct_img = sct.grab(self.region)
                home_dir = os.path.expanduser("~")
                img_path = os.path.join(home_dir, "screenshot_region.png")
                img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
                img.save(img_path)
            print(f"[LOG] Скрин выбранного региона сохранен: {img_path}")

    def capture_region_ocr(self) -> str:
        if not self.region:
            print("[LOG] Регион не задан")
        with mss.mss() as sct:
            sct_img = sct.grab(self.region)
            home_dir = os.path.expanduser("~")
            img_path = os.path.join(home_dir, "screenshot_region.png")
            img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
            img.save(img_path)
        text = self.ocr_model.extract_text(img_path)
        print(f"[LOG] OCR завершен, текст длиной {len(text)} символов")
        return text