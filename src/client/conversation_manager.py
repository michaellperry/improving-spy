#!/usr/bin/env python3
"""Conversation Manager for Spy CLI application."""

from datetime import datetime
from typing import Dict, List, Any, Optional

import logging
from .history_manager import HistoryManager

logger = logging.getLogger(__name__)


class ConversationManager:
    """Manages conversation state and history."""

    def __init__(self):
        self.history_manager = HistoryManager()
        self.conversation_id: Optional[str] = None
        self.messages: List[Dict[str, Any]] = []
        self.selected_spy: Optional[Dict[str, Any]] = None
        self._history_conversations: Optional[List[Dict[str, Any]]] = None
        self._awaiting_history_selection: bool = False

    def set_selected_spy(self, spy_data: Dict[str, Any]) -> None:
        """Set the selected spy and clear conversation state."""
        self.selected_spy = spy_data
        self.conversation_id = None
        self.messages = []
        logger.info(f"Selected spy: {spy_data['name']}")

    def set_conversation_id(self, conversation_id: str) -> None:
        """Set the current conversation ID."""
        self.conversation_id = conversation_id
        logger.info(f"Set conversation ID: {conversation_id}")

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation history."""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        }
        self.messages.append(message)
        logger.debug(f"Added {role} message to conversation")

    def get_conversation_id(self) -> Optional[str]:
        """Get the current conversation ID."""
        return self.conversation_id

    def get_messages(self) -> List[Dict[str, Any]]:
        """Get all messages in the current conversation."""
        return self.messages.copy()

    def get_selected_spy(self) -> Optional[Dict[str, Any]]:
        """Get the currently selected spy."""
        return self.selected_spy

    def has_active_conversation(self) -> bool:
        """Check if there's an active conversation."""
        return self.conversation_id is not None and self.selected_spy is not None

    def save_conversation(self) -> Optional[str]:
        """Save the current conversation to disk."""
        if not self.has_active_conversation() or not self.messages:
            logger.warning("No conversation to save")
            return None

        try:
            spy_id = self.selected_spy["id"]
            filepath = self.history_manager.save_conversation(
                spy_id, self.conversation_id, self.messages
            )
            logger.info(f"Conversation saved to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Error saving conversation: {str(e)}", exc_info=True)
            raise

    def get_conversation_list(self) -> List[Dict[str, Any]]:
        """Get list of saved conversations for the current spy."""
        if not self.selected_spy:
            logger.warning("No spy selected for conversation list")
            return []

        try:
            spy_id = self.selected_spy["id"]
            conversations = self.history_manager.get_conversation_list(spy_id)
            logger.debug(f"Found {len(conversations)} saved conversations")
            return conversations

        except Exception as e:
            logger.error(f"Error loading conversation list: {str(e)}", exc_info=True)
            return []

    def load_conversation(self, filepath: str) -> Dict[str, Any]:
        """Load a conversation from disk."""
        try:
            conversation = self.history_manager.load_conversation(filepath)
            messages = conversation.get("messages", [])

            if not messages:
                raise ValueError("No messages found in the conversation file")

            # Update current state
            self.conversation_id = conversation.get("conversation_id")
            self.messages = messages

            logger.info(f"Loaded conversation from {filepath}")
            return conversation

        except Exception as e:
            logger.error(f"Error loading conversation: {str(e)}", exc_info=True)
            raise

    def set_history_mode(self, conversations: List[Dict[str, Any]]) -> None:
        """Set history selection mode."""
        self._history_conversations = conversations
        self._awaiting_history_selection = True
        logger.debug("Entered history selection mode")

    def is_awaiting_history_selection(self) -> bool:
        """Check if waiting for history selection."""
        return self._awaiting_history_selection

    def get_history_conversations(self) -> Optional[List[Dict[str, Any]]]:
        """Get the list of conversations for history selection."""
        return self._history_conversations

    def clear_history_mode(self) -> None:
        """Clear history selection mode."""
        self._awaiting_history_selection = False
        self._history_conversations = None
        logger.debug("Cleared history selection mode")

    def process_history_selection(self, selection: str) -> Optional[str]:
        """Process a history selection input."""
        if not self._awaiting_history_selection or not self._history_conversations:
            return None

        try:
            index = int(selection) - 1
            if 0 <= index < len(self._history_conversations):
                conversation = self._history_conversations[index]
                filepath = conversation.get("filepath")
                if filepath:
                    self.clear_history_mode()
                    return filepath
                else:
                    logger.error("Conversation filepath not found")
                    return None
            else:
                logger.warning(f"Invalid history selection index: {index}")
                return None

        except ValueError:
            logger.warning(f"Invalid history selection input: {selection}")
            return None
        except Exception as e:
            logger.error(f"Error processing history selection: {str(e)}", exc_info=True)
            return None
