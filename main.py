from screen_monitor import OCRRegion
from gpt_client import review_code
import tkinter as tk
from tkinterweb import HtmlFrame
import re
import markdown2
import time

def markdown_to_html_all_go(md_text):
    html = markdown2.markdown(md_text, extras=["fenced-code-blocks", "code-friendly"])
    html = re.sub(r'<pre><code>', r'<pre><code class="language-go">', html)

    return html

def show_response(text):
    root = tk.Tk()
    root.title("AI response")
    root.geometry("1400x1200")
    root.attributes("-topmost", True)

    frame = HtmlFrame(root, horizontal_scrollbar="auto")
    frame.pack(fill="both", expand=True)

    if isinstance(text, dict) and "error" in text:
        md_html = f"<strong>Ошибка API:</strong> {text['error']['message']}"
    else:
        md_html = markdown_to_html_all_go(str(text))

    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <!-- Highlight.js CSS и JS -->
        <link rel="stylesheet" 
              href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
        <script>hljs.highlightAll();</script>
        <style>
            body {{
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: Consolas, monospace;
                padding: 20px;
                font-weight: normal;
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
            h1, h2, h3, h4, h5, h6 {{
                font-weight: bold;
                color: #ffffff;
            }}
        </style>
    </head>
    <body>
        {md_html}
    </body>
    </html>
    """

    frame.load_html(html)
    root.mainloop()

if __name__ == '__main__':
    ocr = OCRRegion()
    code_text = ocr.capture_region_ocr()
    print("PreciseOCR complete")

    start_time = time.time()
    answer = review_code(code_text)
    end_time = time.time()
    print("Response success")
    print('Elapsed time: ', end_time - start_time)

    show_response(answer)
