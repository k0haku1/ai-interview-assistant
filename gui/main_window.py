from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction, QSlider, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QKeySequence
import markdown2
import re


def markdown_to_html_go(md_text: str) -> str:
    html = markdown2.markdown(md_text, extras=["fenced-code-blocks", "code-friendly"])
    html = re.sub(r'<pre><code>', r'<pre><code class="language-go">', html)
    return f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
        <script>hljs.highlightAll();</script>
        <style>
            body {{ background-color: #1e1e1e; color: #ffffff; font-family: Consolas, monospace; padding: 20px; }}
            pre {{ background: #2d2d2d; padding: 2px; border-radius: 2px; overflow-x: hidden; white-space: pre-wrap; font-size: 14px; }}
            h3 {{ color: #ffffff; }}
            hr {{ border: 1px solid #444; }}
        </style>
    </head>
    <body>{html}</body>
    </html>
    """

class MainWindow(QMainWindow):
    def __init__(self, ocr, ai_client):
        super().__init__()
        self.ocr = ocr
        self.ai_client = ai_client

        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        self.setWindowTitle("AI Interview Tool")
        self.setGeometry(300, 200, 800, 600)
        self.setWindowOpacity(0.75)

        self.setStyleSheet("""
                    QMainWindow {
                        border-left: 0px;
                        border-right: 0px;
                        border-bottom: 0px;
                    }
                """)

        central_widget = QWidget(self)
        central_widget.setContentsMargins(0, 0, 0, 0)
        central_widget.setStyleSheet("background-color: #1e1e1e;")
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.web_view = QWebEngineView(self)
        self.web_view.setStyleSheet("background-color: #1e1e1e; border: none;")
        layout.addWidget(self.web_view)

        self.opacity_slider = QSlider(Qt.Horizontal, self)
        self.opacity_slider.setRange(30, 100)
        self.opacity_slider.setValue(75)
        self.opacity_slider.valueChanged.connect(self.change_opacity)

        self.opacity_slider.setStyleSheet("""
        QSlider {
            background: #1e1e1e;  
            margin: 0px;
            padding: 0px;
        }
        QSlider::groove:horizontal {
            height: 6px;
            background: #2d2d2d;
            border-radius: 3px;
        }
        QSlider::handle:horizontal {
            background: #9b59b6;
            border: none;
            width: 18px;
            height: 18px;
            margin: -6px 0;  
            border-radius: 9px;
        }
        QSlider::handle:horizontal:hover {
            background: #b276d8;
        }
        QSlider::sub-page:horizontal {
            background: #9b59b6;
            border-radius: 3px;
        }
        QSlider::add-page:horizontal {
            background: #2d2d2d;
            border-radius: 3px;
        }
        """)
        layout.addWidget(self.opacity_slider)

        self.setCentralWidget(central_widget)

        action_new_region = QAction(self)
        action_new_region.setShortcut(QKeySequence("Ctrl+Alt+1"))
        action_new_region.triggered.connect(self.capture_and_analyze)
        self.addAction(action_new_region)

        self.html_buffer = ""

    def change_opacity(self, value):
        self.setWindowOpacity(value / 100.0)

    def capture_and_analyze(self):
        self.ocr.select_region()
        print("[LOG] Регион выбран:", self.ocr.region)

        text = self.ocr.capture_region_ocr()
        print("[LOG] OCR текст получен")

        if text.strip():
            print("[LOG] Отправка текста в AI клиент")
            answer = self.ai_client.review_code(text)
            md_html = markdown_to_html_go(str(answer))

            self.html_buffer += f"<h3>===== AI Answer =====</h3>{md_html}<hr>"
            self.web_view.setHtml(self.html_buffer)

    def run(self):
        self.show()