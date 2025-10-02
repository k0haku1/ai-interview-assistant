import time

from ai_clients import DeepSeekClient, DeepSeekAgentClient


class DeepSeekFallbackClient:
    def __init__(self, retries: int = 2, delay: int = 3):
        """
        retries - сколько раз пробовать API перед переключением
        delay   - задержка между попытками (сек)
        """
        self.api_client = DeepSeekClient()
        self.agent_client = DeepSeekAgentClient()
        self.retries = retries
        self.delay = delay

    def review_code(self, code: str) -> str | dict:
        last_error = None

        for attempt in range(1, self.retries + 1):
            try:
                print(f"[INFO] Попытка {attempt}/{self.retries} через API клиент...")
                answer = self.api_client.review_code(code)

                if isinstance(answer, dict) and "error" in answer:
                    last_error = answer["error"]
                    print(f"[WARN] API ошибка: {last_error}")
                else:
                    return answer

            except Exception as e:
                last_error = str(e)
                print(f"[ERROR] Ошибка API клиента (попытка {attempt}): {last_error}")

            if attempt < self.retries:
                print(f"[INFO] Повтор через {self.delay} сек...")
                time.sleep(self.delay)

        print("[INFO] Все попытки API неудачны. Переключение на агент-клиент...")
        return self.agent_client.review_code(code)