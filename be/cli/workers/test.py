import asyncio
import redis.asyncio as redis
import uuid

# Настройка клиента Redis
redis_client = redis.Redis(decode_responses=True)

__source = "console"  # Источник события, для отладки

# Отправка тестового события
async def send_test_event(user_id: int, text: str):
    event_id = str(uuid.uuid4())  # уникальный ID для отладки
    await redis_client.xadd(
        "events",  # имя стрима
        {
            "user_id": str(user_id),
            "text": text,
            "event_id": event_id,
            "source": __source
        }
    )
    print(f"✅ Event sent: {event_id}")

# Отправка тестового события
async def withdraw_gift_event(gift_id: str, user_id: int):
    event_id = str(uuid.uuid4())  # уникальный ID для отладки
    await redis_client.xadd(
        "events",  # имя стрима
        {
            "gift_id": gift_id,
            "user_id": user_id,
            "event_id": event_id,
            "source": __source
        }
    )
    print(f"✅ Event sent: {event_id}")

# Пример запуска
if __name__ == "__main__":
    user_id = input("Введите user_id: ")
    text = input("Введите сообщение: ")
    asyncio.run(withdraw_gift_event("gift_id", "user_id"))

