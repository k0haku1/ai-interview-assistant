from screen_monitor import OCRRegion
from gpt_client import review_code
import tkinter as tk
import time

def show_response (text) :
    root = tk.Tk()
    root.title("AI response")
    root.geometry ("1400x1200")
    root.attributes("-topmost", True)

    text_box = tk.Text(root, wrap="word")
    text_box.pack(expand=True, fill="both")

    if isinstance(text, dict) and "error" in text:
        text_box.insert("1.0", f"Ошибка API:\n{text['error']['message']}")
    else:
        text_box.insert("1.0", str(text))

    root.mainloop()

if __name__ == '__main__':
    ocr = OCRRegion()
    code_text = ocr.capture_region_ocr()
    print("Распознанный текст:\n", code_text)
    start_time = time.time()
    print("Текст с экрана получен",code_text)

    answer = review_code(code_text)
    end_time = time.time()
    print("Ответ GPT получен")
    elapsed_time = end_time - start_time
    print('Elapsed time: ', elapsed_time)

    show_response(answer)

