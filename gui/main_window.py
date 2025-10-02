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
            body {{
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: "Ubuntu", "Cantarell", "Helvetica Neue", Arial, sans-serif;
                padding: 20px;
                font-size: 12px;
                font-weight: 500;
            }}
            pre {{
                background: #2d2d2d;
                padding: 6px;
                border-radius: 4px;
                overflow-x: auto;
                white-space: pre-wrap;
                font-size: 10px;
                font-weight: bold;
            }}
            h3 {{ color: #ffffff; }}
            hr {{ border: 1px solid #444; }}
            ::-webkit-scrollbar {{
                width: 8px;
                height: 8px;
            }}
            ::-webkit-scrollbar-track {{
                background: #1e1e1e;
            }}
            ::-webkit-scrollbar-thumb {{
                background: #555;
                border-radius: 4px;
            }}
            ::-webkit-scrollbar-thumb:hover {{
                background: #777;
            }}
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
        self.setGeometry(300, 200, 900, 600)
        self.setWindowOpacity(0.75)
        self.setStyleSheet("QMainWindow { border: 0px; }")

        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.setStyleSheet("background-color: #1e1e1e;")

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(2)

        self.web_view = QWebEngineView()
        self.web_view.setStyleSheet("background-color: #1e1e1e; border: none;")
        self.web_view.page().setBackgroundColor(QColor("#1e1e1e"))
        self.web_view.setHtml("""
            <html><head><meta charset="UTF-8">
            <style>body { background-color: #1e1e1e; color: #ffffff; }</style>
            </head><body></body></html>
        """)
        left_layout.addWidget(self.web_view)

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(30, 100)
        self.opacity_slider.setValue(75)
        self.opacity_slider.valueChanged.connect(self.change_opacity)
        self.opacity_slider.setStyleSheet("""
            QSlider { background: #1e1e1e; margin: 0; padding: 0; }
            QSlider::groove:horizontal { height: 6px; background: #2d2d2d; border-radius: 3px; }
            QSlider::handle:horizontal { background: #9b59b6; width: 18px; height: 18px; margin: -6px 0; border-radius: 9px; }
            QSlider::handle:horizontal:hover { background: #b276d8; }
            QSlider::sub-page:horizontal { background: #9b59b6; border-radius: 3px; }
            QSlider::add-page:horizontal { background: #2d2d2d; border-radius: 3px; }
        """)
        left_layout.addWidget(self.opacity_slider)

        self.options_button = QPushButton("options")
        self.options_button.setStyleSheet("""
            QPushButton { background-color: #2d2d2d; color: #fff; border: none; padding: 6px; border-radius: 4px; }
            QPushButton:hover { background-color: #3d3d3d; }
        """)
        self.options_button.clicked.connect(self.toggle_options)
        left_layout.addWidget(self.options_button)

        self.option_buttons_widget = QWidget()
        self.option_buttons_layout = QVBoxLayout(self.option_buttons_widget)
        self.option_buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.option_buttons_layout.setSpacing(2)
        for opt in ["result", "code review", "add func", "algorithm", "SQL"]:
            btn = QPushButton(opt)
            btn.setStyleSheet("""
                QPushButton { background-color: #2d2d2d; color: #fff; border: none; padding: 6px; border-radius: 4px; text-align: left; }
                QPushButton:hover { background-color: #3d3d3d; }
            """)
            btn.clicked.connect(lambda checked, o=opt: self.analyze_with_option(o))
            self.option_buttons_layout.addWidget(btn)
        left_layout.addWidget(self.option_buttons_widget)
        self.option_buttons_widget.hide()

        main_splitter.addWidget(left_widget)

        self.chat_widget = ChatWindow(self.local_ai)
        main_splitter.addWidget(self.chat_widget)
        self.chat_widget.hide()  # по умолчанию скрыт

        self.setCentralWidget(main_splitter)

        action = QAction(self)
        action.setShortcut(QKeySequence("Ctrl+Alt+1"))
        action.triggered.connect(self.capture_and_store_text)
        self.addAction(action)

        self.html_buffer = ""
        self.ocr_buffer = ""

        self.chat_button = QPushButton("chat AI", self)
        self.chat_button.setStyleSheet("""
            QPushButton { background-color: #2d2d2d; color: #fff; border: none; padding: 6px; border-radius: 4px; }
            QPushButton:hover { background-color: #3d3d3d; }
        """)
        self.chat_button.clicked.connect(self.toggle_chat)
        left_layout.addWidget(self.chat_button)

    def capture_and_store_text(self):
        self.ocr.select_region()
        self.ocr_buffer = self.ocr.capture_region_ocr()

    def analyze_with_option(self, option: str):
        if self.ocr_buffer.strip():
            answer = self.ai_client.review_code(self.ocr_buffer, option)
            md_html = markdown_to_html_go(str(answer))
            self.html_buffer += f"<h3>===== {option} =====</h3>{md_html}<hr>"
            self.web_view.setHtml(self.html_buffer)

    def toggle_chat(self):
        if self.chat_widget.isVisible():
            self.chat_widget.hide()
            self.chat_button.setText("chat AI")
        else:
            self.chat_widget.show()
            self.chat_button.setText("❌")

    def toggle_options(self):
        if self.option_buttons_widget.isVisible():
            self.option_buttons_widget.hide()
            self.options_button.setText("options")
        else:
            self.option_buttons_widget.show()
            self.options_button.setText("❌")

    def change_opacity(self, value):
        self.setWindowOpacity(value / 100.0)

    def run(self):
        self.show()