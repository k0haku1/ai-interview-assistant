import tkinter as tk
from tkinterweb import HtmlFrame
import markdown2
import re

def markdown_to_html_go(md_text: str) -> str:
    html = markdown2.markdown(md_text, extras=["fenced-code-blocks", "code-friendly"])
    html = re.sub(r'<pre><code>', r'<pre><code class="language-go">', html)
    return html

def show_response(text):
    root = tk.Tk()
    root.title("AI Response")
    root.geometry("1400x1200")
    root.attributes("-topmost", True)

    frame = HtmlFrame(root, horizontal_scrollbar="auto")
    frame.pack(fill="both", expand=True)

    if isinstance(text, dict) and "error" in text:
        md_html = f"<strong>Ошибка API:</strong> {text['error']['message']}"
    else:
        md_html = markdown_to_html_go(str(text))

    html = f"""
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
                font-family: Consolas, monospace;
                padding: 20px;
            }}
            pre, code {{
                font-weight: bold;
                font-size: 14px;
            }}
            pre {{
                background: #2d2d2d;
                padding: 10px;
                border-radius: 8px;
                overflow-x: auto;
            }}
        </style>
    </head>
    <body>{md_html}</body>
    </html>
    """

    frame.load_html(html)
    root.mainloop()