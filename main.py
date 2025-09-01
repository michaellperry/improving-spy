import logging
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.backend.api.routes import router
from src.backend.core.database import init_db

# Create a custom formatter that matches uvicorn's style
class ColouredFormatter(logging.Formatter):
    """Custom formatter that matches uvicorn's colored log format."""
    
    level_name_colors = {
        logging.DEBUG: lambda level_name: f"\033[36m{level_name}\033[0m",  # cyan
        logging.INFO: lambda level_name: f"\033[32m{level_name}\033[0m",   # green
        logging.WARNING: lambda level_name: f"\033[33m{level_name}\033[0m", # yellow
        logging.ERROR: lambda level_name: f"\033[31m{level_name}\033[0m",   # red
        logging.CRITICAL: lambda level_name: f"\033[35m{level_name}\033[0m", # magenta
    }
    
    def format(self, record):
        # Create levelprefix with consistent padding like uvicorn
        levelname = record.levelname
        separator = " " * (8 - len(levelname))
        
        # Color the level name if output is to terminal
        if sys.stdout.isatty():
            color_func = self.level_name_colors.get(record.levelno, lambda x: x)
            levelname = color_func(levelname)
        
        levelprefix = f"{levelname}:{separator}"
        record.levelprefix = levelprefix
        
        # Use uvicorn-style format
        return f"{levelprefix} {record.getMessage()}"

# Configure logging for the backend
LOG_LEVEL = os.environ.get("SPY_LOG_LEVEL", "DEBUG")  # Default to DEBUG
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL.upper()),
    format='%(levelprefix)s %(message)s',
    handlers=[
        logging.StreamHandler(),  # Output to console
    ]
)

# Apply our custom formatter to the root logger
root_logger = logging.getLogger()
for handler in root_logger.handlers:
    handler.setFormatter(ColouredFormatter())

# Set specific logger levels for noisy third-party libraries
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)
logging.getLogger("fastapi").setLevel(logging.INFO)
# Reduce noise from openai client debug messages
logging.getLogger("openai._base_client").setLevel(logging.WARNING)

app = FastAPI(
    title="🕵️ Spy Agent Chat API", 
    version="0.4.0",
    description="""
    # Spy Agent Chat API with WebSockets
    
    This API allows you to chat with spy agents in real-time using WebSockets.
    
    ## WebSocket Endpoints
    
    * `/ws/chat/{spy_id}` - Chat with a spy agent in real-time
    * `/ws/chat/{spy_id}/conversation/{conversation_id}` - Chat with a spy agent using conversation history
    
    ## WebSocket Usage
    
    Connect to a WebSocket endpoint and send JSON messages with the following format:
    
    ```json
    {
        "message": "Your message to the spy agent"
    }
    ```
    
    You will receive JSON responses with the following format:
    
    ```json
    {
        "type": "response",
        "spy_id": "spy-id",
        "spy_name": "Spy Name",
        "message": "Your message",
        "response": "Spy agent's response"
    }
    ```
    
    System messages have the following format:
    
    ```json
    {
        "type": "system",
        "content": "System message"
    }
    ```
    
    Error messages have the following format:
    
    ```json
    {
        "type": "error",
        "content": "Error message"
    }
    ```
    """
)

# Configure CORS for WebSocket support
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize database
init_db()

# Include API routes
app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Spy Agent Chat API! Go to /docs for interactive API and WebSocket documentation."}