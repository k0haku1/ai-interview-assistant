import cv2
import easyocr
import re

class PreciseOCR:
    """
    Класс для точного извлечения текста из изображения.
    Использует easyocr и предварительную обработку изображения.
    """

    def __init__(self, langs=['en', 'ru']):
        self.reader = easyocr.Reader(langs, gpu=True)

    def preprocess_image(self, image_path: str):
        """
        Конвертирует изображение в grayscale и масштабирует его для улучшения распознавания.
        """
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        scale_percent = 150
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        return cv2.resize(img, (width, height), interpolation=cv2.INTER_LINEAR)

    def clean_text(self, text: str) -> str:
        """
        Очищает текст, оставляя только строки с символами, которые могут встречаться в коде.
        """
        lines = text.splitlines()
        cleaned = []
        for line in lines:
            line = line.strip()
            if re.search(r'[A-Za-z0-9{}()\[\];=.+\-/*]', line):
                cleaned.append(line)
        return "\n".join(cleaned)

    def extract_text(self, image_path: str) -> str:
        """
        Извлекает текст из изображения: предварительная обработка -> OCR -> очистка.
        """
        preprocessed = self.preprocess_image(image_path)
        results = self.reader.readtext(preprocessed, detail=0)
        text = "\n".join(results)
        return self.clean_text(text)
