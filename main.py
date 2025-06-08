# consumer.py
import asyncio
import json
from aio_pika import connect_robust, IncomingMessage, ExchangeType

RABBITMQ_URL = "amqp://guest:guest@localhost"  # match Next.js env
QUEUE_NAME = "grading_events"  # match queue passed in publishToQueue

async def process_message(message: IncomingMessage):
    async with message.process():
        try:
            payload = json.loads(message.body.decode())
            print("✅ Received message:", payload)

            # TODO: Process the payload here (e.g., grade essay, save results)

        except Exception as e:
            print("❌ Error processing message:", e)

async def main():
    connection = await connect_robust(RABBITMQ_URL)
    channel = await connection.channel()

    # Declare the queue
    queue = await channel.declare_queue(QUEUE_NAME, durable=True)

    # Start consuming messages
    await queue.consume(process_message)
    print(f"🚀 Waiting for messages in queue: {QUEUE_NAME}")

    return connection

# Keep the consumer running
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    connection = loop.run_until_complete(main())

    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(connection.close())
