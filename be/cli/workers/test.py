import asyncio
import redis.asyncio as redis
import uuid

# Настройка клиента Redis
redis_client = redis.Redis(decode_responses=True)

# Отправка события
async def send_event(user_id: int, text: str):
    event_id = str(uuid.uuid4())  # уникальный ID для отладки
    await redis_client.xadd(
        "events",  # имя стрима
        {
            "user_id": str(user_id),
            "text": text,
            "event_id": event_id,
            "source": "console"
        }
    )
    print(f"✅ Event sent: {event_id}")

# Пример запуска
if __name__ == "__main__":
    user_id = input("Введите user_id: ")
    text = input("Введите сообщение: ")
    asyncio.run(send_event(int(user_id), text))