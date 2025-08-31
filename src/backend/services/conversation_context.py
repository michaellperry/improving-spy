"""Conversation context management for LLM integration.

This module handles formatting conversation history and managing context windows
for the LLM to maintain conversation awareness across multiple messages.
"""

import logging
from typing import Dict, Any, List

# Set up logging
logger = logging.getLogger(__name__)

class ConversationContextManager:
    """Manages conversation context for LLM consumption."""
    
    def __init__(self, max_context_messages: int = 10):
        """Initialize the context manager.
        
        Args:
            max_context_messages: Maximum number of messages to include in context
        """
        self.max_context_messages = max_context_messages
    
    def manage_context_window(self, conversation_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Manage context window by selecting the most relevant messages.
        
        Args:
            conversation_history: List of all conversation messages
            
        Returns:
            List of messages to include in context
        """
        if len(conversation_history) <= self.max_context_messages:
            return conversation_history
        
        # Always include the first message (conversation start) and last few messages
        # This ensures we maintain conversation flow while staying within context limits
        first_message = conversation_history[0]
        recent_messages = conversation_history[-(self.max_context_messages-1):]
        
        return [first_message] + recent_messages
    
    def format_conversation_context(self, conversation_history: List[Dict[str, Any]]) -> str:
        """Format conversation history for LLM consumption.
        
        Args:
            conversation_history: List of message dictionaries
            
        Returns:
            Formatted string representation of conversation history
        """
        if not conversation_history:
            return ""
        
        formatted_messages = []
        for msg in conversation_history:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            
            # Clean and format the content for better LLM consumption
            if content:
                # Remove markdown formatting that might confuse the LLM
                clean_content = content.replace('```', '').replace('**', '').replace('*', '')
                clean_content = clean_content.strip()
                
                if role == 'user':
                    formatted_messages.append(f"User: {clean_content}")
                elif role == 'assistant':
                    formatted_messages.append(f"Assistant: {clean_content}")
                else:
                    formatted_messages.append(f"{role.title()}: {clean_content}")
        
        return "\n".join(formatted_messages)
    
    def create_context_message(self, current_message: str, conversation_context: str) -> str:
        """Create a context-aware message for the LLM.
        
        Args:
            current_message: The current user message
            conversation_context: Formatted conversation history
            
        Returns:
            Message with context for the LLM
        """
        if not conversation_context:
            return current_message
        
        context_message = f"""Previous conversation context:
{conversation_context}

Current message: {current_message}

IMPORTANT: You are continuing an ongoing conversation. Please:
1. Respond to the current message naturally
2. Reference relevant context from the conversation history when appropriate
3. Maintain consistency with your previous responses
4. Stay in character as the spy you are portraying
5. Use any available tools if explicitly requested

Please respond to the current message while considering the conversation context above."""
        
        return context_message
