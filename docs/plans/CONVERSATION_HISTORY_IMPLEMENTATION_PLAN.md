# Conversation History with LLM Implementation Plan

## Overview
This plan addresses the critical gap where the application stores conversation history but never sends it to the LLM, preventing the AI agents from maintaining context across multiple messages. The goal is to implement a simple conversation management system where each spy selection creates a new conversation and the LLM receives conversation history for context.

## Progress Summary
- ✅ **Phase 1: Backend Conversation Management** - COMPLETED
- ✅ **Phase 2: LLM Context Integration** - COMPLETED  
- ❌ **Phase 3: Frontend Integration** - PENDING

**Current Status**: Phase 2 completed - LLM now receives conversation history for context awareness. Agent service properly manages context windows and formats conversation history for optimal LLM consumption. The backend conversation endpoints are fully functional with context-aware chat capabilities.

## Prerequisites
- [x] Backend server running (`uv run uvicorn main:app --port 8000 --reload`)
- [x] Database initialized with conversation tables
- [x] Frontend CLI accessible (`uv run python run_cli.py`)
- [x] Ollama running locally with qwen2.5:14b-instruct model

## Phase 1: Backend Conversation Management ✅

### 1.1 Conversation Creation Endpoint
**Location**: `src/backend/api/routes.py`

**Required Steps**:
- [x] Add `POST /api/conversations` endpoint to create new conversations
- [x] Endpoint accepts `spy_id` and returns `conversation_id`
- [x] Store spy_id with conversation in database
- [x] Ensure conversation repository creates conversation records

**Files Modified**:
- `src/backend/api/routes.py` - Added conversation creation endpoint
- `src/backend/repositories/conversation_repository.py` - Already functional

### 1.2 Chat with Conversation Context
**Location**: `src/backend/api/routes.py`

**Required Steps**:
- [x] Modify chat endpoint to use `conversation_id` instead of `spy_id`
- [x] Retrieve conversation history by `conversation_id`
- [x] Get spy_id from conversation record
- [x] Send conversation history to LLM for context

**Files Modified**:
- `src/backend/api/routes.py` - Added `/chat/conversation/{conversation_id}` endpoint
- `src/backend/services/agent.py` - Added `chat_with_context` method
- `src/backend/models/__init__.py` - Added `ConversationCreate` model

**Testing Approach**:
- [x] Unit tests for conversation creation and retrieval
- [x] Integration tests for chat with conversation context
- [x] Manual validation: Create conversation, send messages, verify history

### 1.3 Acceptance Criteria
**Functional Requirements**:
- [x] New conversation created when spy is selected
- [x] Chat endpoint uses conversation_id for routing
- [x] Conversation history retrieved and sent to LLM
- [x] Spy_id stored with conversation for context
- [x] Proper error handling for invalid conversation IDs

**Testing Approach**:
- [x] Unit tests for conversation endpoints
- [x] Integration tests for conversation flow
- [x] Manual validation: Test conversation creation and chat flow
- [x] Error handling tests: Invalid conversation IDs

**Implementation Details**:
- Added `POST /api/conversations` endpoint for conversation creation
- Added `POST /api/chat/conversation/{conversation_id}` endpoint for context-aware chat
- Maintained backward compatibility with existing `/api/chat/{spy_id}` endpoint
- Added `ConversationCreate` Pydantic model for conversation creation
- Enhanced `ChatAgent` with `chat_with_context` method for conversation history
- Conversation history is automatically stored and retrieved for LLM context

## Phase 2: LLM Context Integration ✅

### 2.1 Agent Service Update
**Location**: `src/backend/services/agent.py`

**Required Steps**:
- [x] Modify `ChatAgent.chat()` method to accept conversation history
- [x] Format conversation history for LLM consumption
- [x] Include history in AI model requests
- [x] Handle context window limitations

**Files Modified**:
- `src/backend/services/agent.py` - Updated to use ConversationContextManager
- `src/backend/services/conversation_context.py` - New file for context management

### 2.2 Message History Formatting
**Location**: `src/backend/services/conversation_context.py`

**Required Steps**:
- [x] Format conversation messages for LLM context
- [x] Implement role-based message structure (user/assistant)
- [x] Add basic context window management
- [x] Ensure tool calling works with conversation history

**Testing Approach**:
- [x] Unit tests for message formatting
- [x] Integration tests for LLM with conversation context
- [x] Manual validation: Multi-turn conversations with context
- [x] Tool calling tests with conversation history

### 2.3 Acceptance Criteria
**Functional Requirements**:
- [x] LLM receives conversation history for context
- [x] Messages formatted correctly for AI consumption
- [x] Context window handled gracefully
- [x] Tool calling works with conversation context
- [x] Spies maintain conversation memory

**Testing Approach**:
- [x] Unit tests for message formatting and context
- [x] Integration tests for LLM integration
- [x] Manual validation: Verify context in AI responses
- [x] Performance tests with various conversation lengths

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
1. **Immediate**: ✅ Phase 1 (Backend Conversation Management) - COMPLETED
2. **Short-term**: ✅ Phase 2 (LLM Context Integration) - COMPLETED
3. **Medium-term**: Complete Phase 3 (Frontend Integration)
