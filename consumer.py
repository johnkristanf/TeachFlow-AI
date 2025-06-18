import json
import traceback
import os
import asyncio
import logging

from aio_pika.abc import AbstractRobustConnection
from aio_pika.exceptions import AMQPConnectionError
from aio_pika import connect_robust, IncomingMessage

from utils.essay import clean_essay_text
from services.essay_grading import EssayGradingService
from retry import retry_message_queue
from exceptions import RETRYABLE_EXCEPTIONS



essay_service = EssayGradingService()
MAX_RETRIES = 3
    
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
                rubric_category = payload.get("rubric_category")
                grade_level = payload.get("grade_level")
                grade_intensity = payload.get("grade_intensity")
                
                print(f'essay_id: {essay_id}')
                print(f'rubric_category: {rubric_category}')
                print(f'grade_level: {grade_level}')
                print(f'grade_intensity: {grade_intensity}')
                
                clean_essay = clean_essay_text(essay_text)
                print(f'clean_essay: {clean_essay}')
                essay_service.grade_essay(essay_id, clean_essay, rubric_category, grade_level, grade_intensity, rubric_criteria)
                
        except Exception as e: 
            logging.critical(f"Error occured in message consumption: {e}")
            traceback.print_exc() # Always print full traceback for debugging

            # Prepare common error details
            error_details = {
                "original_exception_type": type(e).__name__,
                "stack_trace": traceback.format_exc(),
            }
            
            is_retryable = isinstance(e, RETRYABLE_EXCEPTIONS)

            if is_retryable:
                print(f"🔁 Caught a retryable error.")
                if retries < MAX_RETRIES:
                    print(f"Attempting retry {retries + 1}/{MAX_RETRIES} for essay {essay_id}.")
                    await retry_message_queue(message, retries)
                else:
                    logging.critical(f"💥 Max retries ({MAX_RETRIES}) exhausted for essay {essay_id}. Logging as failed.")
                    failure_type = 'RETRY_EXHAUSTED'
                    error_message = f"Max retries ({MAX_RETRIES}) exhausted. Error: {e}"
                    essay_service.set_failed_grading(
                        essay_id,
                        failure_type,
                        error_message,
                        error_details=error_details,
                    )
                    await message.reject(requeue=False) # Send to DLQ
            else:
                logging.critical(f"❌ Caught a non-retryable error.")
                failure_type = 'PERMANENT_ERROR'
                error_message = f"Non-retryable error during grading: {e}"

                essay_service.set_failed_grading(
                    essay_id,
                    failure_type,
                    error_message,
                    error_details=error_details,
                )
                
                await message.reject(requeue=False) # Send to DLQ

async def start_rabbitmq_consumer():
    
    connection: AbstractRobustConnection = None
    RABBITMQ_URL = os.getenv("RABBITMQ_URL") 
    QUEUE_NAME = "grading_events"  

    for attempt in range(5):
        try:
            connection = await connect_robust(RABBITMQ_URL)
            if not connection.is_closed:
                logging.info("✅ Successfully connected to RabbitMQ.")
                break
            else:
                logging.warning("⚠️ RabbitMQ connection is closed.")
                
        except AMQPConnectionError as e:
            logging.warning(f"[Attempt {attempt + 1}] RabbitMQ not ready: {e}")
            await asyncio.sleep(5)
    else:
        raise RuntimeError("RabbitMQ is still not reachable after 5 attempts.")
    
    channel = await connection.channel()
    
    # 1. Declare the Dead Letter Exchange (DLX)
    dlx_name = 'grading_dlx'
    await channel.declare_exchange(dlx_name, 'topic', durable=True)
   
   
   # 2. Declare the Dead Letter Queue (DLQ)
    dlq_name = 'grading_dlq'
    dlq = await channel.declare_queue(dlq_name, durable=True)
    
    # 3. Bind the DLQ to the DLX
    await dlq.bind(dlx_name, 'failed_grading')

    # Declare the main queue, linking it to the DLX
    args = {"x-dead-letter-exchange": dlx_name, "x-dead-letter-routing-key": "failed_grading"}
    queue = await channel.declare_queue(QUEUE_NAME, durable=True, arguments=args)

    # Start consuming messages
    await queue.consume(process_message)
    logging.info(f"🚀 Waiting for messages in queue: {QUEUE_NAME}")

    return connection