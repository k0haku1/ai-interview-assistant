import requests
import time
import json
from config import DEEPSEEK_API_KEY

class DeepSeekClient:
    def __init__(self):
        self.endpoint = "https://api.intelligence.io.solutions/api/v1/chat/completions"
        self.messages = [
            {
                "role": "system",
                "content": (
                    "Ты AI-помощник для собеседований по программированию. "
                    "Отвечай строго на русском языке во всех случаях, даже для SQL, Go или алгоритмов. "
                    "У тебя две задачи: "
                    "1) Если на входе код — проведи код ревью: оцени стиль, архитектуру, эффективность, возможные ошибки. "
                    "   Дай рекомендации по разделению ответственности у функций/структур и предложи улучшения. "
                    "Особенно внимательно смотри со стороны многгопоточки и оптимизации работы горутин"
                    "2) Если на входе алгоритмическая задача — реши её на Go. "
                    "   Обязательно: добавь построчные комментарии к коду (как в ревью Pull Request). "
                    "   В комментариях объясни, что делает каждая ключевая строка. "
                    "   После кода объясни общий ход решения и оцени сложность (по времени и памяти). "
                    "   При возможности предложи, как сэкономить ресурсы (например, оптимизация памяти или времени). "
                    "3) Если на входе задача на SQL (создание таблиц или запрос) — ориентируйся на PostgreSQL. "
                        "Для выборки давай два варианта:\n"
                        "   a) Простой, читаемый вариант — для понимания логики.\n"
                        "   b) Оптимизированный вариант через JOIN/агрегаты — чтобы работал быстрее на больших таблицах.\n"
                        "В комментариях объясняй, что делает каждая ключевая строка, и указывай, где лучше использовать каждый вариант.\n\n"
                    "Отвечай структурированно, без лишней воды."
                )
            }
        ]

    def review_code(self, code: str) -> str | dict:
        self.messages.append({
            "role": "user",
            "content": f"Есть код или алгоритм:\n{code} Если это код — проведи ревью. Если это алгоритм — реши его на Go, добавь построчные комментарии в код и объясни решение. Если задача на SQL то напиши запрос (создание таблиц, выборка данных или группировка)"
        })
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8", "messages": self.messages, "temperature": 0.3}

        print("[DEBUG] Отправка запроса к DeepSeek API...")

        try:
            start_time = time.time()
            resp = requests.post(self.endpoint, headers=headers, json=data, timeout=30)
            resp.raise_for_status()
            duration = time.time() - start_time

            print(f"[DEBUG] Ответ получен за {duration:.2f} сек, статус: {resp.status_code}")
            answer = resp.json()['choices'][0]['message']['content']
            self.messages.append({"role": "assistant", "content": answer})
            return answer
        except requests.exceptions.Timeout:
            print("[ERROR] Тайм-аут при обращении к API")
            return {"error": "Timeout при обращении к DeepSeek API"}
        except Exception as e:
            print("[ERROR] Ошибка при запросе к API:", str(e))
            return {"error": str(e)}
