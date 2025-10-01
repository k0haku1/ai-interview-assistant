from PyQt5.QtWidgets import (
    QMainWindow, QTextEdit, QAction, QSlider, QVBoxLayout, QWidget,
    QPushButton, QSplitter, QApplication
)
from .chat_gui import ChatWindow
from PyQt5.QtCore import Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtGui import QKeySequence, QColor
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
    def __init__(self, ocr, ai_client, local_ai=None):
        super().__init__()
        self.ocr = ocr
        self.ai_client = ai_client
        self.local_ai = local_ai

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

        splitter = QSplitter(Qt.Horizontal)
        splitter.setStyleSheet("background-color: #1e1e1e;")

        left_widget = QWidget(self)
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(0)

        self.web_view = QWebEngineView(self)
        self.web_view.setStyleSheet("background-color: #1e1e1e; border: none;")
        self.web_view.page().setBackgroundColor(QColor("#1e1e1e"))
        self.web_view.setHtml("""
            <html>
            <head><meta charset="UTF-8">
            <style>body { background-color: #1e1e1e; color: #ffffff; }</style>
            </head><body></body></html>
        """)
        left_layout.addWidget(self.web_view)

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
        left_layout.addWidget(self.opacity_slider)

        self.chat_button = QPushButton("Открыть чат", self)
        self.chat_button.setStyleSheet("""
                   QPushButton {
                       background-color: #2d2d2d;
                       color: #ffffff;
                       border: none;
                       padding: 6px;
                       border-radius: 4px;
                   }
                   QPushButton:hover {
                       background-color: #3d3d3d;
                   }
               """)
        self.chat_button.clicked.connect(self.toggle_chat)
        left_layout.addWidget(self.chat_button)

        splitter.addWidget(left_widget)

        self.chat_widget = ChatWindow(self.local_ai)
        splitter.addWidget(self.chat_widget)
        self.chat_widget.hide()

        self.setCentralWidget(splitter)

        action_new_region = QAction(self)
        action_new_region.setShortcut(QKeySequence("Ctrl+Alt+1"))
        action_new_region.triggered.connect(self.capture_and_analyze)
        self.addAction(action_new_region)

        self.html_buffer = ""

    def toggle_chat(self):
        if self.chat_widget.isVisible():
            self.chat_widget.hide()
            self.chat_button.setText("Открыть чат")
        else:
            self.chat_widget.show()
            self.chat_button.setText("Закрыть чат")

    def change_opacity(self, value):
        self.setWindowOpacity(value / 100.0)

    def capture_and_analyze(self):
        self.ocr.select_region()
        text = self.ocr.capture_region_ocr()
        if text.strip():
            answer = self.ai_client.review_code(text)
            md_html = markdown_to_html_go(str(answer))
            self.html_buffer += f"<h3>===== AI Answer =====</h3>{md_html}<hr>"
            self.web_view.setHtml(self.html_buffer)

    def run(self):
        self.show()