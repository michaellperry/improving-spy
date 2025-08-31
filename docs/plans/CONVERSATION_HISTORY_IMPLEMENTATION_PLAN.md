# Conversation History with LLM Implementation Plan

## Overview
This plan addresses the critical gap where the application stores conversation history but never sends it to the LLM, preventing the AI agents from maintaining context across multiple messages. The goal is to implement a simple conversation management system where each spy selection creates a new conversation and the LLM receives conversation history for context.

## Progress Summary
- ❌ **Phase 1: Backend Conversation Management** - PENDING
- ❌ **Phase 2: LLM Context Integration** - PENDING  
- ❌ **Phase 3: Frontend Integration** - PENDING

**Current Status**: Application has conversation storage infrastructure but LLM never receives conversation history, limiting context awareness.

## Prerequisites
- [ ] Backend server running (`uv run uvicorn main:app --port 8000 --reload`)
- [ ] Database initialized with conversation tables
- [ ] Frontend CLI accessible (`uv run python run_cli.py`)
- [ ] Ollama running locally with qwen2.5:14b-instruct model

## Phase 1: Backend Conversation Management ✅

### 1.1 Conversation Creation Endpoint
**Location**: `src/backend/api/routes.py`

**Required Steps**:
- [ ] Add `POST /api/conversations` endpoint to create new conversations
- [ ] Endpoint accepts `spy_id` and returns `conversation_id`
- [ ] Store spy_id with conversation in database
- [ ] Ensure conversation repository creates conversation records

**Files to Modify**:
- `src/backend/api/routes.py` - Add conversation creation endpoint
- `src/backend/repositories/conversation_repository.py` - Ensure create method works

### 1.2 Chat with Conversation Context
**Location**: `src/backend/api/routes.py`

**Required Steps**:
- [ ] Modify chat endpoint to use `conversation_id` instead of `spy_id`
- [ ] Retrieve conversation history by `conversation_id`
- [ ] Get spy_id from conversation record
- [ ] Send conversation history to LLM for context

**Testing Approach**:
- [ ] Unit tests for conversation creation and retrieval
- [ ] Integration tests for chat with conversation context
- [ ] Manual validation: Create conversation, send messages, verify history

### 1.3 Acceptance Criteria
**Functional Requirements**:
- [ ] New conversation created when spy is selected
- [ ] Chat endpoint uses conversation_id for routing
- [ ] Conversation history retrieved and sent to LLM
- [ ] Spy_id stored with conversation for context
- [ ] Proper error handling for invalid conversation IDs

**Testing Approach**:
- [ ] Unit tests for conversation endpoints
- [ ] Integration tests for conversation flow
- [ ] Manual validation: Test conversation creation and chat flow
- [ ] Error handling tests: Invalid conversation IDs

## Phase 2: LLM Context Integration ✅

### 2.1 Agent Service Update
**Location**: `src/backend/services/agent.py`

**Required Steps**:
- [ ] Modify `ChatAgent.chat()` method to accept conversation history
- [ ] Format conversation history for LLM consumption
- [ ] Include history in AI model requests
- [ ] Handle context window limitations

**Files to Modify**:
- `src/backend/services/agent.py` - Update chat method for conversation history
- `src/backend/models/__init__.py` - Add message history models if needed

### 2.2 Message History Formatting
**Location**: `src/backend/services/agent.py`

**Required Steps**:
- [ ] Format conversation messages for LLM context
- [ ] Implement role-based message structure (user/assistant)
- [ ] Add basic context window management
- [ ] Ensure tool calling works with conversation history

**Testing Approach**:
- [ ] Unit tests for message formatting
- [ ] Integration tests for LLM with conversation context
- [ ] Manual validation: Multi-turn conversations with context
- [ ] Tool calling tests with conversation history

### 2.3 Acceptance Criteria
**Functional Requirements**:
- [ ] LLM receives conversation history for context
- [ ] Messages formatted correctly for AI consumption
- [ ] Context window handled gracefully
- [ ] Tool calling works with conversation context
- [ ] Spies maintain conversation memory

**Testing Approach**:
- [ ] Unit tests for message formatting and context
- [ ] Integration tests for LLM integration
- [ ] Manual validation: Verify context in AI responses
- [ ] Performance tests with various conversation lengths

## Phase 3: Frontend Integration ✅

### 3.1 Spy Selection Flow
**Location**: `src/client/spy_cli.py`

**Required Steps**:
- [ ] Clear chat history when spy is selected
- [ ] Call conversation creation endpoint
- [ ] Store conversation_id for subsequent chats
- [ ] Update chat flow to use conversation_id

**Files to Modify**:
- `src/client/spy_cli.py` - Update spy selection and chat flow
- `src/client/api_client.py` - Add conversation creation method
- `src/client/screens/main.py` - Update main screen if needed

### 3.2 Chat with Conversation Context
**Location**: `src/client/spy_cli.py`

**Required Steps**:
- [ ] Send chat messages with conversation_id
- [ ] Maintain conversation_id across message exchanges
- [ ] Handle conversation state properly
- [ ] Update UI to show conversation context

**Testing Approach**:
- [ ] Unit tests for conversation state management
- [ ] Integration tests for frontend-backend communication
- [ ] Manual validation: End-to-end conversation flow
- [ ] Error handling tests: Network failures, invalid states

### 3.3 Acceptance Criteria
**Functional Requirements**:
- [ ] Chat history cleared on spy selection
- [ ] New conversation created automatically
- [ ] Messages sent with conversation context
- [ ] Conversation state maintained across messages
- [ ] UI reflects conversation context properly

**Testing Approach**:
- [ ] Unit tests for conversation flow
- [ ] Integration tests for complete flow
- [ ] Manual validation: Test spy selection and chat flow
- [ ] UI tests: Verify conversation display

## Success Criteria
- [ ] LLM receives conversation history for context awareness
- [ ] Spies maintain conversation memory across multiple messages
- [ ] Frontend creates new conversations on spy selection
- [ ] Chat uses conversation_id for routing and context
- [ ] Simple, maintainable conversation management

## Testing Strategy

### Unit Testing
- **Backend**: Test conversation endpoints and agent service
- **Frontend**: Test conversation state management
- **Models**: Test conversation data structures

### Integration Testing
- **End-to-End**: Complete flow from spy selection to multi-turn chat
- **API Integration**: Test conversation endpoints with database
- **LLM Integration**: Verify conversation context in AI responses

### Manual Validation
- **User Experience**: Test spy selection and conversation flow
- **Error Scenarios**: Network failures, invalid data
- **Cross-Session**: Verify conversations persist during session

## Implementation Notes

### Key Design Decisions
1. **Simple Flow**: Spy selection → New conversation → Chat with context
2. **Conversation-Centric**: Chat endpoint uses conversation_id, not spy_id
3. **Automatic Management**: Frontend handles conversation creation automatically
4. **Context Preservation**: LLM receives full conversation history for context

### Dependencies
- Backend conversation repository must be functional
- LLM integration must support conversation context
- Frontend must handle conversation state properly

## Next Steps
1. **Immediate**: Implement Phase 1 (Backend Conversation Management)
2. **Short-term**: Complete Phase 2 (LLM Context Integration)
3. **Medium-term**: Finish Phase 3 (Frontend Integration)
