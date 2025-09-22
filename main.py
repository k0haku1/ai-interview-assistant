from ocr import OCRRegion
from ai_clients import DeepSeekClient
from ai_clients import AiLocalClient
from gui import MainWindow

def main():
    ocr = OCRRegion()
    ai_client = DeepSeekClient()
    window = MainWindow(ocr, ai_client)
    window.run()

    # aiClient = AiLocalClient()
    # aiClient.answer("Что ты знаешь про map в гоу и их устройство")

if __name__ == "__main__":
    main()