from PyQt5.QtWidgets import QMainWindow, QTextEdit, QAction
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
            pre {{ background: #2d2d2d; padding: 10px; border-radius: 8px; overflow-x: auto; font-size: 14px; }}
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

        self.setWindowTitle("AI Interview Tool")

        self.setGeometry(300, 200, 800, 600)

        self.setWindowOpacity(0.65)


        self.web_view = QWebEngineView(self)
        self.setCentralWidget(self.web_view)

        action_new_region = QAction(self)
        action_new_region.setShortcut(QKeySequence("Ctrl+Alt+1"))
        action_new_region.triggered.connect(self.capture_and_analyze)
        self.addAction(action_new_region)

        self.html_buffer = ""

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