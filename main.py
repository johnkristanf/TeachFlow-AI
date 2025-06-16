import asyncio
import uvicorn
from contextlib import asynccontextmanager
from consumer import start_rabbitmq_consumer 
from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(start_rabbitmq_consumer())
    yield
    
app = FastAPI(lifespan=lifespan)

            
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
