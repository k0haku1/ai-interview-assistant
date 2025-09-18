from tkinter import Tk, Button
from gui.markdown_viewer import show_response

class MainWindow:
    def __init__(self, ocr, ai_client):
        """
        ocr — объект OCRRegion
        ai_client — объект AI-клиента (DeepSeek, LocalAI и т.д.)
        """
        self.ocr = ocr
        self.ai_client = ai_client
        self.root = Tk()
        self.root.title("AI Interview Tool")
        self.root.geometry("400x200")

        # Кнопка для захвата кода и получения ответа AI
        self.capture_btn = Button(self.root, text="Capture & Analyze", command=self.capture_and_analyze)
        self.capture_btn.pack(pady=20)

    def capture_and_analyze(self):
        """
        Захватывает текст с экрана, отправляет AI и отображает результат.
        """
        code_text = self.ocr.capture_region_ocr()
        answer = self.ai_client.review_code(code_text)
        show_response(answer)

    def run(self):
        self.root.mainloop()