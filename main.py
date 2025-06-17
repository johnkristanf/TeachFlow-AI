import uvicorn
import sys
from contextlib import asynccontextmanager
from consumer import start_rabbitmq_consumer 
from fastapi import FastAPI

        
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🐇 Initializing RabbitMQ Consumer...")
    try:
        # Pass the app instance or a flag to the consumer setup if needed
        consumer_connection = await start_rabbitmq_consumer()
        print("📡 RabbitMQ consumer started successfully.")
        # You can store the connection on the app state if you need it elsewhere
        app.state.rabbitmq_connection = consumer_connection
    except Exception as e:
        # Log the critical failure and exit
        print(f"❌ CRITICAL: Failed to start RabbitMQ consumer: {e}")
        # Optionally add more detailed logging here
        # Exit the application process to make the failure obvious
        sys.exit(1)

    yield
    # Graceful shutdown logic
    print("🐇 Shutting down RabbitMQ connection...")
    if app.state.rabbitmq_connection:
        await app.state.rabbitmq_connection.close()
    print("✅ RabbitMQ connection closed.")

    
app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
