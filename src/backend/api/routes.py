import logging
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session

from ..services.agent import ChatAgent
from ..core.database import get_db
from ..models import ChatRequest, ChatResponse, Spy, SpyCreate, ConversationCreate
from ..repositories.conversation_repository import ConversationRepository
from ..repositories.spy_repository import SpyRepository

# Set up logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["Chat"])

# Initialize repositories

# Dependency that provides a ChatAgent instance for the spy.
def get_agent(spy_id: str, db: Session = Depends(get_db)) -> ChatAgent:
    """Dependency that provides a ChatAgent instance for the spy.
    
    Args:
        spy_id: The spy's ID (primary key from database)
    """
    logger.info(f"Getting agent for spy_id: {spy_id}")
    repo = SpyRepository(db)
    
    # Get spy by ID (primary key)
    spy = repo.get(spy_id)
    logger.info(f"Result from repo.get: {spy}")
    
    if not spy:
        logger.error(f"Spy not found for ID: {spy_id}")
        raise HTTPException(status_code=404, detail=f"Spy not found: {spy_id}")
    
    logger.info(f"Found spy: {spy}")
    
    # Convert Pydantic model to dict for ChatAgent
    spy_dict = spy.model_dump()
    logger.info(f"Spy dict: {spy_dict}")
    
    return ChatAgent(spy_dict)

# -------------------------------
# Conversation Management Endpoints
# -------------------------------

@router.post("/conversations", status_code=status.HTTP_201_CREATED)
def create_conversation(
    spy_id: str = Form(...),
    db: Session = Depends(get_db)
):
    """Create a new conversation for a spy."""
    logger.info(f"Creating new conversation for spy_id: {spy_id}")
    
    try:
        # Verify spy exists
        spy_repo = SpyRepository(db)
        spy = spy_repo.get(spy_id)
        if not spy:
            raise HTTPException(status_code=404, detail=f"Spy not found: {spy_id}")
        
        # Create conversation
        conversation_repo = ConversationRepository(db)
        new_conversation = conversation_repo.create_conversation(spy_id)
        
        logger.info(f"Created conversation {new_conversation['id']} for spy {spy_id}")
        return {
            "conversation_id": new_conversation["id"],
            "spy_id": spy_id,
            "message": "Conversation created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating conversation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error creating conversation: {str(e)}"
        )

# -------------------------------
# Spy CRUD Endpoints
# -------------------------------

@router.get("/spies/", response_model=List[Spy])
def list_spies(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """List all spies with pagination"""
    repo = SpyRepository(db)
    return repo.list(skip=skip, limit=limit)

@router.post("/spies/", response_model=Spy, status_code=status.HTTP_201_CREATED)
def create_spy(
    spy: SpyCreate,
    db: Session = Depends(get_db)
):
    """Create a new spy"""
    repo = SpyRepository(db)
    db_spy = repo.create(spy.model_dump())
    return db_spy

@router.get("/spies/{spy_id}", response_model=Spy)
def get_spy(
    spy_id: str,
    db: Session = Depends(get_db)
):
    """Get a spy by ID"""
    repo = SpyRepository(db)
    spy = repo.get(spy_id)
    if not spy:
        raise HTTPException(status_code=404, detail="Spy not found")
    return spy

@router.get("/spies/codename/{codename}", response_model=Spy)
def get_spy_by_codename(
    codename: str,
    db: Session = Depends(get_db)
):
    """Get a spy by codename"""
    repo = SpyRepository(db)
    spy = repo.get_by_codename(codename)
    if not spy:
        raise HTTPException(status_code=404, detail=f"Spy with codename '{codename}' not found")
    return spy

@router.put("/spies/{spy_id}", response_model=Spy)
def update_spy(
    spy_id: str,
    spy_update: Spy,
    db: Session = Depends(get_db)
):
    """Update a spy"""
    repo = SpyRepository(db)
    db_spy = repo.update(spy_id, spy_update.dict())
    if not db_spy:
        raise HTTPException(status_code=404, detail="Spy not found")
    return db_spy

@router.delete("/spies/{spy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_spy(
    spy_id: str,
    db: Session = Depends(get_db)
):
    """Delete a spy"""
    repo = SpyRepository(db)
    if not repo.delete(spy_id):
        raise HTTPException(status_code=404, detail="Spy not found")
    return None

# -------------------------------
# Chat Endpoints
# -------------------------------

@router.post("/chat/conversation/{conversation_id}", response_model=ChatResponse)
async def chat_with_conversation(
    conversation_id: str, 
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """
    Chat with a spy agent using conversation context.
    
    The conversation_id is used to retrieve conversation history and send it to the LLM
    for context awareness across multiple messages.
    """
    logger.info(f"Received chat request for conversation_id: {conversation_id}")
    try:
        # Initialize conversation repository
        logger.info("Initializing conversation repository...")
        conversation_repository = ConversationRepository(db)
        logger.info("Conversation repository initialized")

        # Get conversation and verify it exists
        logger.info(f"Retrieving conversation: {conversation_id}")
        conversation = conversation_repository.get_conversation(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail=f"Conversation not found: {conversation_id}")
        
        spy_id = conversation["spy_id"]
        logger.info(f"Found conversation for spy_id: {spy_id}")

        try:
            # Get the agent
            logger.info(f"Getting agent for spy_id: {spy_id}")
            agent = get_agent(spy_id, db)
            logger.info("Agent initialized successfully")
            
            # Get conversation history for context
            logger.info("Retrieving conversation history for context")
            conversation_history = conversation_repository.get_message_history(conversation_id)
            logger.info(f"Retrieved {len(conversation_history)} messages from conversation history")
            
            # Send message to agent with conversation context
            logger.info("Sending message to agent with conversation context...")
            result = await agent.chat_with_context(
                message=request.message,
                conversation_history=conversation_history
            )
            logger.info("Received response from agent")
            
            # Store the user message and agent response in conversation history
            logger.info("Storing messages in conversation history")
            conversation_repository.add_message(conversation_id, "user", request.message)
            conversation_repository.add_message(conversation_id, "assistant", result.get("response", ""))
            
            # Return response with conversation context
            response = {
                "spy_id": result.get("spy_id", ""),
                "spy_name": result.get("spy_name", "Unknown"),
                "message": request.message,
                "response": result.get("response", ""),
                "tool_calls": result.get("tool_calls", []),
                "conversation_id": conversation_id
            }
            logger.info("Sending response back to client")
            return response
            
        except HTTPException as he:
            logger.error(f"HTTP Exception in chat processing: {str(he)}")
            raise
        except Exception as e:
            logger.error(f"Error in chat processing: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error processing chat: {str(e)}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat_with_conversation: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing chat request: {str(e)}"
        )
