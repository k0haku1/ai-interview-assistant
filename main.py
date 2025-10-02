from ocr import OCRRegion
import sys
import time
from ai_clients import DeepSeekClient, DeepSeekFallbackClient
from ai_clients import DeepSeekAgentClient
from PyQt5.QtWidgets import QApplication
from ai_clients import AiLocalClient
from gui import MainWindow

def main():
    start_main = time.time()
    print(f"[{time.strftime('%H:%M:%S')}] Создание QApplication...")
    app = QApplication(sys.argv)
    print(f"[{time.strftime('%H:%M:%S')}] QApplication создан")

    print(f"[{time.strftime('%H:%M:%S')}] Инициализация OCRRegion...")
    ocr = OCRRegion()
    print(f"[{time.strftime('%H:%M:%S')}] OCRRegion инициализирован")

    print(f"[{time.strftime('%H:%M:%S')}] Инициализация AI клиента...")
    ai_client = DeepSeekFallbackClient(retries=2, delay=3)
    print(f"[{time.strftime('%H:%M:%S')}] AI клиент готов")


    print(f"[{time.strftime('%H:%M:%S')}] AI-local клиент готов")
    local_ai = AiLocalClient()
    print(f"[{time.strftime('%H:%M:%S')}] Создание MainWindow...")
    window = MainWindow(ocr, ai_client, local_ai)
    window.show()
    print(f"[{time.strftime('%H:%M:%S')}] MainWindow готов. GUI запущен.")

    exit_code = app.exec_()
    end_main = time.time()
    print(f"[{time.strftime('%H:%M:%S')}] Программа завершена. Время выполнения main: {end_main - start_main:.2f} сек")
    sys.exit(exit_code)


# aiClient = AiLocalClient()
    # aiClient.answer("Что ты знаешь про map в гоу и их устройство")

if __name__ == "__main__":
    main()
