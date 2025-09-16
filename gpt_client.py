import requests
from config import DEEPSEEK_API_KEY

messages = [
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

ENDPOINT = "https://api.intelligence.io.solutions/api/v1/chat/completions"


def review_code(code: str) -> str | None:
    global messages

    messages.append({
    "role": "user",
    "content": f"""
Есть блок кода или алгоритм:

{code}

Если это код — проведи ревью.
Если это алгоритм — реши его на Go, добавь построчные комментарии в код и объясни решение.
"""
})

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    data = {
        "model": "Intel/Qwen3-Coder-480B-A35B-Instruct-int4-mixed-ar",
        "messages": messages,
        "temperature": 0.3,
    }
    #"model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",

    try:
        response = requests.post(ENDPOINT, headers=headers, json=data)
        response.raise_for_status()
        json_resp = response.json()

        answer = json_resp['choices'][0]['message']['content']
        messages.append({"role": "assistant", "content": answer})
        return answer

    except requests.exceptions.HTTPError:
        print(f"HTTP ошибка {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Ошибка при запросе к AI: {e}")

    return None