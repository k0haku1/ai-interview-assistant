import requests
import json

class AiLocalClient:
    def __init__(self, model: str = "qwen3_assistant"):
        self.endpoint = "http://localhost:11434/api/chat"
        self.model = model
        self.messages = []

    def answer_stream(self, question: str):
        """
        Потоковый генератор ответа.
        Возвращает частичные куски текста по мере генерации.
        """
        # Сохраняем сообщение пользователя
        self.messages.append({"role": "user", "content": question})

        response = requests.post(
            self.endpoint,
            json={"model": self.model, "messages": self.messages},
            stream=True
        )

        full_answer = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                if "message" in data:
                    chunk = data["message"]["content"]
                    full_answer += chunk
                    yield full_answer  # отдаём всё, что есть на данный момент
                if data.get("done"):
                    break

        # Сохраняем финальный ответ в историю
        self.messages.append({"role": "assistant", "content": full_answer})
        yield full_answer  # финальный кусок