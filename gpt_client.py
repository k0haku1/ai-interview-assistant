import requests
from config import DEEPSEEK_API_KEY

messages = [
    {
        "role": "system",
        "content": "Ты AI-помощник для собеседований. Анализируй код, давай рекомендации по код ревью и решай алгоритмические задачи максимально эффективно с объяснением шагов."
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

Если это код — проведи ревью и дай рекомендации по стилю, эффективности, возможным ошибкам (обрати внимание на разделение ответственности у классов/структур).
Если это алгоритмическая задача — реши её, приведи пример реализации и объясни ход решения (не забудь про сложность алгоритма).
"""
    })

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    data = {
        "model": "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
        "messages": messages,
        "temperature": 0.3,
    }

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