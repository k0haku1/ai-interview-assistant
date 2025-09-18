from ocr import OCRRegion
from ai_clients import DeepSeekClient
from gui import MainWindow

def main():
    ocr = OCRRegion()
    ai_client = DeepSeekClient()
    window = MainWindow(ocr, ai_client)
    window.run()

if __name__ == "__main__":
    main()