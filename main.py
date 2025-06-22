import uvicorn
import sys
import logging
from contextlib import asynccontextmanager
from consumer import start_rabbitmq_consumer 
from fastapi import FastAPI

        
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("🐇 Initializing RabbitMQ Consumer...")
    try:
        consumer_connection = await start_rabbitmq_consumer()
        app.state.rabbitmq_connection = consumer_connection
    except Exception as e:
        logging.critical(f"❌ CRITICAL: Failed to start RabbitMQ consumer: {e}", exc_info=True)
        sys.exit(1)

    yield
    # Graceful shutdown logic
    logging.info("🐇 Shutting down RabbitMQ connection...")
    if app.state.rabbitmq_connection:
        await app.state.rabbitmq_connection.close()
    logging.info("✅ RabbitMQ connection closed.")

    
app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
