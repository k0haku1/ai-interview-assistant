from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton, QApplication
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWebEngineWidgets import QWebEngineView
import markdown2
import re
import uuid

def markdown_to_html_go(md_text: str) -> str:
    html = markdown2.markdown(md_text, extras=["fenced-code-blocks", "code-friendly"])
    html = re.sub(r'<pre><code>', r'<pre><code class="language-go">', html)
    return html

class AIWorker(QThread):
    partial_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, ai_client, question):
        super().__init__()
        self.ai_client = ai_client
        self.question = question

    def run(self):
        full_answer = ""
        for partial in self.ai_client.answer_stream(self.question):
            full_answer = partial
            self.partial_signal.emit(full_answer)
        self.finished_signal.emit()

class ChatWindow(QWidget):
    def __init__(self, local_ai):
        super().__init__()
        self.local_ai = local_ai
        self.chat_buffer = ""
        self.workers = {}

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        self.chat_history = QWebEngineView(self)
        self.chat_history.setStyleSheet("background-color: #1e1e1e; border: none;")
        self.chat_history.page().setBackgroundColor(QColor("#1e1e1e"))
        layout.addWidget(self.chat_history)

        self.chat_history.setHtml("""
                <html>
                <head>
                    <meta charset="UTF-8">
                    <style>
                        body { background-color:#1e1e1e; color:#ffffff; font-family:Consolas, monospace; padding:10px; font-size:12px; }
                    </style>
                </head>
                <body></body>
                </html>
                """)

        self.chat_input = QTextEdit(self)
        self.chat_input.setFixedHeight(50)
        self.chat_input.setStyleSheet("background-color: #2d2d2d; color: #ffffff; font-size:12px;")
        layout.addWidget(self.chat_input)

        self.send_button = QPushButton("Отправить", self)
        self.send_button.setStyleSheet(
            "QPushButton { background-color:#9b59b6; color:#fff; border:none; padding:6px; border-radius:4px; }"
            "QPushButton:hover { background-color:#b276d8; }"
        )
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

    def _render_html(self, buffer: str) -> str:
        return f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
            <script>
                document.addEventListener("DOMContentLoaded", function() {{
                    hljs.highlightAll();
                    window.scrollTo(0, document.body.scrollHeight);
                }});
            </script>
            <style>
                body {{
                    background-color:#1e1e1e; 
                    color:#ffffff; 
                    font-family:Consolas, monospace; 
                    padding:10px; 
                    font-size:12px; 
                }}
                pre {{
                    background:#2d2d2d; 
                    padding:6px; 
                    border-radius:4px; 
                    overflow-x:auto; 
                    white-space:pre-wrap; 
                    font-size:10px; 
                    font-weight:bold;
                }}
                h1,h2,h3,h4,h5,h6 {{ color:#ffffff; }}
                p {{ margin:4px 0; font-size:12px; }}
            </style>
        </head>
        <body>{buffer}</body>
        </html>
        """

    def add_message(self, sender: str, text: str, color: str, assistant_id=None):
        id_attr = f'id="{assistant_id}"' if assistant_id else ''
        bubble = f"""
        <div {id_attr} style="
            margin:6px 0;
            padding:8px 12px;
            background-color:{color};
            border-radius:8px;
            max-width:80%;
            word-wrap:break-word;
        ">{text}</div>
        """
        align = "right" if sender == "user" else "left"
        self.chat_buffer += f'<div style="text-align:{align};">{bubble}</div>'
        self.chat_history.setHtml(self._render_html(self.chat_buffer))

    def send_message(self):
        user_text = self.chat_input.toPlainText().strip()
        if not user_text or not self.local_ai:
            return

        self.chat_input.clear()
        self.add_message("user", user_text, "#2d2d2d")

        assistant_id = str(uuid.uuid4())
        thinking_text = "..."
        self.add_message("assistant", thinking_text, "#444", assistant_id=assistant_id)
        QApplication.processEvents()

        worker = AIWorker(self.local_ai, user_text)
        worker.partial_signal.connect(lambda text, aid=assistant_id: self.update_partial_append(text, aid))
        worker.finished_signal.connect(lambda aid=assistant_id: self.finalize_assistant_message(aid))
        self.workers[assistant_id] = worker
        worker.start()

    def update_partial_append(self, text, assistant_id):
        self.chat_buffer = re.sub(
            rf'(<div id="{assistant_id}".*?>)(.*?)(</div>)',
            lambda m: f"{m.group(1)}{text}{m.group(3)}",
            self.chat_buffer,
            flags=re.DOTALL
        )
        self.chat_history.setHtml(self._render_html(self.chat_buffer))

    def finalize_assistant_message(self, assistant_id):
        worker_text = ""
        match = re.search(rf'<div id="{assistant_id}".*?>(.*?)</div>', self.chat_buffer, flags=re.DOTALL)
        if match:
            worker_text = match.group(1)

        if "Краткий ответ:" in worker_text:
            worker_text = worker_text.split("Краткий ответ:")[-1].strip()

        formatted = markdown_to_html_go(worker_text)

        self.chat_buffer = re.sub(
            rf'<div id="{assistant_id}".*?>.*?</div>',
            '',
            self.chat_buffer,
            flags=re.DOTALL
        )
        self.add_message("assistant", formatted, "#444")

        if assistant_id in self.workers:
            del self.workers[assistant_id]