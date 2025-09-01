#!/usr/bin/env python3
"""Event Handler for Spy CLI application."""

import logging
from typing import Dict, Any, Optional
import os
from .widgets import ChatWindow

logger = logging.getLogger(__name__)


class EventHandler:
    """Handles user interactions and events."""

    def __init__(self, app, ui_manager, conversation_manager, websocket_manager):
        self.app = app
        self.ui_manager = ui_manager
        self.conversation_manager = conversation_manager
        self.websocket_manager = websocket_manager

    async def handle_spy_selection(self, spy_data: Dict[str, Any]) -> None:
        """Handle spy selection event."""
        logger.debug(f"Handling spy selection: {spy_data['name']}")

        try:
            # Update conversation manager
            self.conversation_manager.set_selected_spy(spy_data)

            # Create new conversation
            logger.debug("Creating new conversation for selected spy")
            conv = await self.app.api_client.create_conversation(spy_data["id"])
            conversation_id = conv.get("conversation_id")
            self.conversation_manager.set_conversation_id(conversation_id)
            logger.info(f"New conversation created: {conversation_id}")

            # Setup chat UI
            await self.ui_manager.setup_chat_ui(spy_data)

            # Add welcome message
            self.ui_manager.add_welcome_message(spy_data)
            self.conversation_manager.add_message(
                "system",
                f"I'm {spy_data['name']}, codename {spy_data['codename']}. How can I assist you?",
            )

            # Connect to WebSocket
            logger.debug("Starting WebSocket connection")
            self.app.run_worker(
                self.websocket_manager.connect(spy_data["id"], conversation_id)
            )

            logger.debug("Spy selection process completed successfully")

        except Exception as e:
            logger.error(f"Error in spy selection: {str(e)}", exc_info=True)
            self.ui_manager.show_error(f"Error selecting spy: {str(e)}")

    async def handle_message_submission(self, message: str) -> None:
        """Handle message submission event."""
        if not message.strip():
            return

        selected_spy = self.conversation_manager.get_selected_spy()
        if not selected_spy:
            return

        spy_id = selected_spy["id"]
        chat_window = self.ui_manager.get_chat_window()

        # Add user message to chat
        chat_window.add_message(message, is_user=True)
        self.conversation_manager.add_message("user", message)

        try:
            # Clear input
            self.ui_manager.clear_input()

            # Show typing indicator
            chat_window.show_typing()

            # Update connection status
            self.ui_manager.update_connection_status("Sending message...")

            # Send the message
            conversation_id = self.conversation_manager.get_conversation_id()
            if not conversation_id:
                raise RuntimeError(
                    "No conversation ID available. Please select a spy first."
                )

            response = await self.app.api_client.chat_with_history(
                spy_id=spy_id, conversation_id=conversation_id, message=message
            )

            # Process the response
            chat_window.add_message(response["response"], is_user=False)
            self.conversation_manager.add_message("assistant", response["response"])
            self.ui_manager.update_connection_status("Connected")

        except ConnectionError as e:
            error_msg = str(e)
            self.ui_manager.update_connection_status("Connection Error")
            chat_window.add_message(f"🔴 {error_msg}", is_user=False)
            logger.error(f"Connection error: {error_msg}")

        except Exception as e:
            error_msg = f"Error sending message: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.ui_manager.update_connection_status("Error (see chat)")
            chat_window.add_message(error_msg, is_user=False)

        finally:
            # Always remove typing indicator
            chat_window.hide_typing()

    def handle_focused_spy_selection(self) -> None:
        """Handle focused spy selection via keyboard."""
        logger.debug("Enter key pressed in main app")

        if not self.conversation_manager.get_selected_spy():
            try:
                logger.debug("No spy selected yet, looking for spy selector")
                spy_selector = self.app.query_one("#spy-selector")
                logger.debug(f"Found spy selector: {spy_selector}")

                if hasattr(spy_selector, "action_select_focused"):
                    logger.debug("Calling action_select_focused on spy selector")
                    spy_selector.action_select_focused()
                else:
                    logger.warning(
                        "SpySelector doesn't have action_select_focused method"
                    )

            except Exception as e:
                logger.error(f"Error in focused spy selection: {str(e)}", exc_info=True)

    async def handle_save_conversation(self) -> None:
        """Handle conversation save action."""
        if not self.conversation_manager.has_active_conversation():
            self.ui_manager.show_error("No conversation to save")
            return

        try:
            filepath = self.conversation_manager.save_conversation()
            if filepath:
                chat_window = self.ui_manager.get_chat_window()
                chat_window.add_message(
                    f"Conversation saved to {os.path.basename(filepath)}", is_user=False
                )

        except Exception as e:
            error_msg = f"Error saving conversation: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.ui_manager.show_error(error_msg)

    async def handle_show_history(self) -> None:
        """Handle show history action."""
        if not self.conversation_manager.get_selected_spy():
            self.ui_manager.show_error("Please select a spy first")
            return

        try:
            conversations = self.conversation_manager.get_conversation_list()

            if not conversations:
                self.ui_manager.show_error("No saved conversations found")
                return

            # Display conversation list
            chat_window = self.ui_manager.get_chat_window()
            chat_window.add_message("Available conversations:", is_user=False)

            for i, conv in enumerate(conversations[:10]):  # Show up to 10 most recent
                date_str = (
                    conv["date"].split("T")[0] if conv["date"] else "Unknown date"
                )
                chat_window.add_message(
                    f"{i+1}. {date_str} - {conv['message_count']} messages",
                    is_user=False,
                )

            chat_window.add_message(
                "Type the number of the conversation to load (e.g., '1'):",
                is_user=False,
            )

            # Set history mode
            self.conversation_manager.set_history_mode(conversations)

        except Exception as e:
            error_msg = f"Error loading conversation history: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.ui_manager.show_error(error_msg)

    async def handle_load_conversation(self, filepath: str) -> None:
        """Handle conversation loading."""
        try:
            # Load the conversation
            conversation = self.conversation_manager.load_conversation(filepath)
            messages = conversation.get("messages", [])

            if not messages:
                self.ui_manager.show_error("No messages found in the conversation file")
                return

            # Clear the current chat window
            chat_container = self.app.query_one("#chat-container")
            chat_container.remove_children()

            # Get avatar from codename
            selected_spy = self.conversation_manager.get_selected_spy()
            abbrev = "".join(
                [word[0] for word in selected_spy["codename"].split() if word]
            )

            # Create and mount new chat window
            chat_window = ChatWindow(selected_spy["name"], abbrev)
            chat_container.mount(chat_window)
            self.ui_manager.chat_window = chat_window

            # Add messages to the chat window
            for msg in messages:
                role = msg.get("role", "")
                content = msg.get("content", "")

                if role == "user":
                    chat_window.add_message(content, is_user=True)
                elif role in ["assistant", "system"]:
                    chat_window.add_message(content, is_user=False)

            # Add a system message indicating the conversation was loaded
            load_msg = f"Loaded conversation from {os.path.basename(filepath)}"
            chat_window.add_message(load_msg, is_user=False)
            logger.info(f"Loaded conversation from {filepath}")

        except Exception as e:
            error_msg = f"Error loading conversation: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.ui_manager.show_error(error_msg)

    def handle_history_selection(self, selection: str) -> Optional[str]:
        """Handle history selection input."""
        return self.conversation_manager.process_history_selection(selection)

    def handle_clear_input(self) -> None:
        """Handle clear input action."""
        self.ui_manager.clear_input()
        logger.debug("Input field cleared via keyboard shortcut")

    def handle_show_help(self) -> None:
        """Handle show help action."""
        self.ui_manager.show_help()

    def handle_toggle_chat_mode(self) -> None:
        """Handle chat mode toggle (kept for compatibility)."""
        logger.debug("Chat mode toggle is no longer supported")
