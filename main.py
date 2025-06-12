import asyncio
import json
import traceback
from aio_pika import connect_robust, IncomingMessage
from utils.essay import clean_essay_text
from services.essay_grading import EssayGradingService
from retry import retry_message_queue
from exceptions import RETRYABLE_EXCEPTIONS

RABBITMQ_URL = "amqp://guest:guest@localhost"  # match Next.js env
QUEUE_NAME = "grading_events"  # match queue passed in publishToQueue
MAX_RETRIES = 3

essay_service = EssayGradingService()

async def process_message(message: IncomingMessage):
    async with message.process(ignore_processed=True):
        try:
            payload = json.loads(message.body.decode())
            retries = message.headers.get("x-retry", 0)
            print(f'retries: {retries}')
            
            event = payload.get('event')
            essay_id = payload.get("essay_id")

            # TODO: Process the payload here (e.g., grade essay, save results)
            if event == 'ESSAY_SUBMITTED':
                essay_text = payload.get("essay_text")
                rubric_criteria = payload.get("rubric_criteria")
                
                clean_essay = clean_essay_text(essay_text)
                essay_service.grade_essay(essay_id, essay_text, rubric_criteria)
                
                print(f'essay_id: {essay_id}')
                print(f'clean_essay: {clean_essay}')
                print(f'rubric_criteria: {rubric_criteria}')
            
        except RETRYABLE_EXCEPTIONS as e:
            print("🔁 Retryable error occurred:", e)
            if retries < MAX_RETRIES:
                await retry_message_queue(message, retries)
            else:
                print("💥 Max retries exceeded. Dropping message.")
                essay_service.set_failed_grading(essay_id)
                await message.reject(requeue=False)

        except Exception as e:
            print("❌ Non-retryable error:", e)
            traceback.print_exc()
            essay_service.set_failed_grading(essay_id)
            await message.reject(requeue=False)

            

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
