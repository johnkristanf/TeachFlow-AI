import asyncio

import io
import cv2
import uvicorn
import numpy as np

from contextlib import asynccontextmanager
from consumer import main as start_rabbitmq_consumer  
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(start_rabbitmq_consumer())
    yield
    

app = FastAPI(lifespan=lifespan)

@app.post("/enhance")
async def enhance_image(file: UploadFile = File(...)):
    content = await file.read()
    npimg = np.frombuffer(content, np.uint8)
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)   
     
    # Denoise while preserving edges
    denoised = cv2.fastNlMeansDenoising(gray, h=15)
    # Histogram equalization for contrast
    equalized = cv2.equalizeHist(denoised)
    
    upscaled = cv2.resize(equalized, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

    thresh = cv2.adaptiveThreshold(
        upscaled, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        15,
        8
    )

    # Optional: Slight Gaussian blur to remove jagged noise
    blurred = cv2.GaussianBlur(thresh, (1, 1), 0)

    _, encoded = cv2.imencode('.png', blurred)
    return StreamingResponse(io.BytesIO(encoded.tobytes()), media_type="image/png")
        
            
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
