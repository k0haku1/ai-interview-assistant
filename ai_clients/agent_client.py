import os
import asyncio
from iointel import Agent, Workflow
from config import DEEPSEEK_API_KEY  # твой ключ

class DeepSeekAgentClient:
    def __init__(self):
        self.messages = [
            {
                "role": "system",
                "content": (
                    "Ты AI-помощник для собеседований по программированию. "
                    "Отвечай строго на русском языке во всех случаях, даже для SQL, Go или алгоритмов. "
                    "У тебя две задачи: "
                    "1) Если на входе код — проведи код ревью: оцени стиль, архитектуру, эффективность, возможные ошибки. "
                    "   Дай рекомендации по разделению ответственности у функций/структур и предложи улучшения. "
                    "Особенно внимательно смотри со стороны многгопоточки и оптимизации работы горутин. "
                    "2) Если на входе алгоритмическая задача — реши её на Go. "
                    "   Обязательно: добавь построчные комментарии к коду (как в ревью Pull Request). "
                    "   В комментариях объясни, что делает каждая ключевая строка. "
                    "   После кода объясни общий ход решения и оцени сложность (по времени и памяти). "
                    "   При возможности предложи, как сэкономить ресурсы (например, оптимизация памяти или времени). "
                    "3) Если на входе задача на SQL (создание таблиц или запрос) — ориентируйся на PostgreSQL. "
                    "Для выборки давай два варианта: простой и оптимизированный через JOIN/агрегаты. "
                    "В комментариях объясняй каждую ключевую строку и где использовать каждый вариант.\n\n"
                    "Форматируй ответы в Markdown с fenced code blocks, особенно для Go и SQL."
                )
            }
        ]

        self.agent = Agent(
            name="DeepSeek Agent",
            instructions="Используй системные сообщения для контекста. Отвечай в Markdown, сохраняй построчные комментарии для кода.",
            model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.intelligence.io.solutions/api/v1"
        )

    async def _run_workflow(self, code: str):
        # Сохраняем историю сообщений для агента
        conversation_history = "\n".join(
            [m["content"] for m in self.messages if m["role"] in ("system", "user")]
        )

        workflow = Workflow(objective=conversation_history + "\n" + code, client_mode=False)
        results = await workflow.custom(
            name="custom-task",
            objective=code,
            instructions="Используй предыдущий контекст и инструкции агента, отвечай в Markdown, соблюдая построчные комментарии для кода",
            agents=[self.agent],
        ).run_tasks()
        # Возвращаем результат как Markdown текст
        answer = results["results"]["custom-task"]
        # Сохраняем ответ в истории сообщений
        self.messages.append({"role": "assistant", "content": answer})
        return answer

    def review_code(self, code: str) -> str | dict:
        self.messages.append({
            "role": "user",
            "content": f"Есть код или алгоритм:\n{code} Если это код — проведи ревью. "
                       "Если это алгоритм — реши его на Go, добавь построчные комментарии в код и объясни решение. "
                       "Если задача на SQL, то напиши запрос (создание таблиц, выборка данных или группировка)."
        })
        try:
            return asyncio.run(self._run_workflow(code))
        except Exception as e:
            print("[ERROR] Ошибка при запуске агент-клиента:", str(e))
            return {"error": str(e)}