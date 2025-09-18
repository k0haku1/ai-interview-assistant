import requests
from config import DEEPSEEK_API_KEY

class DeepSeekClient:
    def __init__(self):
        self.endpoint = "https://api.intelligence.io.solutions/api/v1/chat/completions"
        self.messages = [
            {
                "role": "system",
                "content": (
                    "Ты AI-помощник для собеседований по программированию. "
                    "У тебя две задачи: "
                    "1) Если на входе код — проведи код ревью: оцени стиль, архитектуру, эффективность, возможные ошибки. "
                    "   Дай рекомендации по разделению ответственности у функций/структур и предложи улучшения. "
                    "2) Если на входе алгоритмическая задача — реши её на Go. "
                    "   Обязательно: добавь построчные комментарии к коду (как в ревью Pull Request). "
                    "   В комментариях объясни, что делает каждая ключевая строка. "
                    "   После кода объясни общий ход решения и оцени сложность (по времени и памяти). "
                    "   При возможности предложи, как сэкономить ресурсы (например, оптимизация памяти или времени). "
                    "Отвечай структурированно, без лишней воды."
                )
            }
        ]

    def review_code(self, code: str) -> str | dict:
        self.messages.append({
            "role": "user",
            "content": f"Есть код или алгоритм:\n{code} Если это код — проведи ревью. Если это алгоритм — реши его на Go, добавь построчные комментарии в код и объясни решение."
        })
        headers = {"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8", "messages": self.messages, "temperature": 0.3}

        try:
            resp = requests.post(self.endpoint, headers=headers, json=data)
            resp.raise_for_status()
            answer = resp.json()['choices'][0]['message']['content']
            self.messages.append({"role": "assistant", "content": answer})
            return answer
        except Exception as e:
            return {"error": str(e)}
