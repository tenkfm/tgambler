import asyncio
import redis.asyncio as redis

REDIS_STREAM = "events"
REDIS_GROUP = "bot-group"
REDIS_CONSUMER = "bot-1"

redis_client = redis.Redis(decode_responses=True)


async def setup_redis():
    try:
        await redis_client.xgroup_create(
            name=REDIS_STREAM,
            groupname=REDIS_GROUP,
            id='0',
            mkstream=True
        )
    except redis.ResponseError as e:
        if "BUSYGROUP" not in str(e):
            raise


async def listen_redis(app):
    await setup_redis()
    print("👂 Redis listening started")
    while True:
        try:
            result = await redis_client.xreadgroup(
                groupname=REDIS_GROUP,
                consumername=REDIS_CONSUMER,
                streams={REDIS_STREAM: '>'},
                count=10,
                block=5000
            )
            if result:
                for _, messages in result:
                    for msg_id, msg in messages:
                        print("📨 New message from Redis:", msg)
                        user_id = msg.get("user_id")
                        text = msg.get("text")
                        if user_id and text:
                            await app.bot.send_message(chat_id=int(user_id), text=text)
                        await redis_client.xack(REDIS_STREAM, REDIS_GROUP, msg_id)
        except Exception as e:
            print("❌ Redis error:", e)
            await asyncio.sleep(3)
