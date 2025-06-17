import asyncio
import traceback
import uvicorn
from contextlib import asynccontextmanager
from consumer import start_rabbitmq_consumer 
from fastapi import FastAPI


async def run_rabbitmq_consumer():
    try:
        await start_rabbitmq_consumer()
    except Exception as e:
        print(f"❌ Background task failed: {e}")
        traceback.print_exc()
        
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🐇 Initializing RabbitMQ Consumer...")
    try:
        asyncio.create_task(run_rabbitmq_consumer())
    except Exception as e:
        print(f"❌ Failed to start RabbitMQ consumer: {e}")
    yield
    
app = FastAPI(lifespan=lifespan)

            
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
