from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from inference import ask_question
import uvicorn
import logging
import asyncio
from functools import partial

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Woofie Chat API")

# Add CORS middleware with more specific configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your Next.js frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    confidence: float
    source: str

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    logger.info(f"Headers: {request.headers}")
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "message": "An error occurred while processing your request. Please try again later."
            }
        )

@app.get("/")
async def root():
    return {"status": "healthy", "service": "woofie-chat"}

@app.options("/api/chat")
async def options_chat():
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "http://localhost:3000",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
        }
    )

@app.get("/api/chat")
async def get_chat():
    logger.info("Received GET request to /api/chat - This endpoint only accepts POST requests")
    return JSONResponse(
        status_code=405,
        content={
            "error": "Method Not Allowed",
            "message": "This endpoint only accepts POST requests. Please use POST to send chat messages."
        },
        headers={
            "Allow": "POST, OPTIONS",
            "Access-Control-Allow-Origin": "http://localhost:3000",
        }
    )

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        logger.info(f"Received chat request: {request.message}")
        
        # Run the chat processing in a thread pool with a timeout
        loop = asyncio.get_event_loop()
        try:
            results = await asyncio.wait_for(
                loop.run_in_executor(None, partial(ask_question, request.message)),
                timeout=30.0  # 30 second timeout
            )
        except asyncio.TimeoutError:
            logger.error("Request timed out after 30 seconds")
            return ChatResponse(
                response="I'm sorry, the request took too long to process. Please try again.",
                confidence=0.0,
                source="timeout"
            )
        
        if not results:
            return ChatResponse(
                response="I'm sorry, I couldn't find a specific answer to your question. Could you please rephrase or ask something else?",
                confidence=0.0,
                source="fallback"
            )
        
        # Get the best matching result
        best_result = results[0]
        
        response = ChatResponse(
            response=best_result["answer"],
            confidence=best_result["score"],
            source=best_result["source"]
        )
        logger.info(f"Sending response: {response}")
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return ChatResponse(
            response="I'm sorry, I encountered an error while processing your request. Please try again.",
            confidence=0.0,
            source="error"
        )

if __name__ == "__main__":
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
