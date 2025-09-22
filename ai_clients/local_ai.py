import requests
import json

class AiLocalClient:
    def __init__(self, model: str = "qwen3_assistant"):
        self.endpoint = "http://localhost:11434/api/chat"
        self.model = model
        self.messages = []

    def answer(self, question: str):
        self.messages.append({
            "role": "user",
            "content": question
        })

        response = requests.post(
            self.endpoint,
            json={"model": self.model, "messages": self.messages},
            stream=True
        )

        print("\n response:\n")
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode("utf-8"))
                if "message" in data:
                    print(data["message"]["content"], end="", flush=True)
                if data.get("done"):
                    break
        print("\n--- end ---\n")

        self.messages.append({
            "role": "assistant",
            "content": data.get("message", {}).get("content", "")
        })