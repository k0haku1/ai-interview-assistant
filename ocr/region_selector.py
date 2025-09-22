import sys
import json
import os
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen
import mss
from PIL import Image

from .precise_ocr import PreciseOCR

REGION_FILE = "region.json"

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
        with open(REGION_FILE, "w") as f:
            json.dump(self.region, f)
        print("Новая область для OCR:", self.region)
        self.close()

    def paintEvent(self, event):
        if self.start and self.end:
            painter = QPainter(self)
            pen = QPen(Qt.red, 2)
            painter.setPen(pen)
            painter.drawRect(QRect(self.start, self.end))


class OCRRegion:
    def __init__(self):
        self.region = {}
        self.load_region()
        self.ocr_model = PreciseOCR()

    def load_region(self):
        if os.path.exists(REGION_FILE):
            with open(REGION_FILE, "r") as f:
                self.region = json.load(f)

    def select_region(self):
        app = QApplication(sys.argv)
        selector = RegionSelector()
        selector.show()
        app.exec_()
        self.region = selector.region

    def capture_region_ocr(self) -> str:
        if not self.region:
            self.select_region()
        with mss.mss() as sct:
            sct_img = sct.grab(self.region)
            img_path = "screenshot_region.png"
            img = Image.frombytes("RGB", sct_img.size, sct_img.rgb)
            img.save(img_path)

        return self.ocr_model.extract_text(img_path)
