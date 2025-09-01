#!/usr/bin/env python3
"""UI Manager for Spy CLI application."""

import logging
from typing import Dict, Any, Optional
from textual.containers import Container
from textual.widgets import Static

from .widgets.spy_selector import SpySelector
from .widgets import ChatWindow, InputBar

logger = logging.getLogger(__name__)


class UIManager:
    """Manages UI setup and component interactions."""

    def __init__(self, app):
        self.app = app
        self.chat_window: Optional[ChatWindow] = None
        self.input_bar: Optional[InputBar] = None
        self.spy_selector: Optional[SpySelector] = None

    async def setup_initial_ui(self, spies: list) -> None:
        """Set up the initial UI after loading data."""
        logger.debug("Setting up initial UI")

        # Remove loading message
        loading_message = self.app.query_one("#loading-message")
        if loading_message:
            loading_message.remove()

        # Create main UI
        main_container = self.app.query_one("#main-container")

        # Spy selector
        self.spy_selector = SpySelector(
            spies, self.app.on_spy_selected, id="spy-selector"
        )
        main_container.mount(self.spy_selector)
        logger.debug(f"Mounted SpySelector with ID: {self.spy_selector.id}")

        # Add welcome message to sidebar
        welcome = Static("\nWelcome to Spy Chat\n", classes="section-title")
        sidebar = Container(id="sidebar")
        main_container.mount(sidebar)
        sidebar.mount(welcome)

        # Add connection status
        self.connection_status = Static("Status: Connecting...", id="connection-status")
        sidebar.mount(self.connection_status)

        # Chat container (initially hidden)
        main_container.mount(Container(id="chat-container"))

        # Input container (initially hidden)
        input_container = Container(id="input-container")
        main_container.mount(input_container)
        self.input_bar = InputBar(self.app.on_message_submitted)
        self.input_bar.id = "message-input"
        input_container.mount(self.input_bar)

    async def setup_chat_ui(self, spy_data: Dict[str, Any]) -> None:
        """Set up the chat UI for a selected spy."""
        logger.debug(f"Setting up chat UI for spy: {spy_data['name']}")

        try:
            # Remove the spy selector if it exists
            if self.spy_selector:
                logger.debug("Removing spy selector")
                await self.spy_selector.remove()
                self.spy_selector = None
                logger.debug("Successfully removed spy selector")

            # Get or create chat container
            chat_container = self.app.query_one("#chat-container")
            if not chat_container:
                logger.debug("Chat container not found, creating one")
                main_container = self.app.query_one("#main-container")
                if not main_container:
                    raise RuntimeError("Main container not found")
                chat_container = Container(id="chat-container")
                main_container.mount(chat_container)
                await self.app.refresh_layout()
                logger.debug("Created and mounted chat container")
            else:
                # Clear existing chat UI if any
                logger.debug("Clearing existing chat UI")
                await chat_container.remove_children()
                await self.app.refresh_layout()
                logger.debug("Cleared chat container")

            # Create chat window
            abbrev = "".join([word[0] for word in spy_data["codename"].split() if word])
            self.chat_window = ChatWindow(spy_data["name"], abbrev)
            chat_container.mount(self.chat_window)

            # Show input container
            input_container = self.app.query_one("#input-container")
            if input_container and not input_container.has_class("visible"):
                input_container.add_class("visible")

            # Focus the message input
            if self.input_bar:
                self.input_bar.focus()

            logger.debug("Chat UI setup completed successfully")

        except Exception as e:
            logger.error(f"Error setting up chat UI: {e}", exc_info=True)
            raise

    def add_welcome_message(self, spy_data: Dict[str, Any]) -> None:
        """Add welcome message to chat window."""
        if not self.chat_window:
            logger.error("Chat window not available for welcome message")
            return

        welcome_msg = (
            f"I'm {spy_data['name']}, codename {spy_data['codename']}. "
            "How can I assist you?"
        )
        logger.debug(f"Adding welcome message: {welcome_msg}")
        self.chat_window.add_message(welcome_msg, is_user=False)

    def update_connection_status(self, status: str) -> None:
        """Update the connection status display."""
        if hasattr(self, "connection_status") and self.connection_status:
            self.connection_status.update(f"Status: {status}")

    def get_chat_window(self) -> Optional[ChatWindow]:
        """Get the current chat window."""
        return self.chat_window

    def get_input_bar(self) -> Optional[InputBar]:
        """Get the current input bar."""
        return self.input_bar

    def clear_input(self) -> None:
        """Clear the input field."""
        if self.input_bar:
            self.input_bar.value = ""
            logger.debug("Input field cleared")

    def show_error(self, message: str) -> None:
        """Display an error message in the chat window."""
        try:
            if self.chat_window:
                self.chat_window.add_message(f"Error: {message}", is_user=False)
            else:
                # Fallback to notification if chat window not available
                self.app.notify(message, severity="error")
        except Exception as e:
            logger.error(f"Error showing error message: {str(e)}", exc_info=True)
            # Final fallback to print
            print(f"Error: {message}")

    def show_help(self) -> None:
        """Show help information in chat window."""
        if not self.chat_window:
            return

        help_text = """
        Keyboard Shortcuts:
        -----------------
        Ctrl+Q: Quit the application
        Ctrl+S: Send the current message
        Ctrl+C: Clear the input field
        Ctrl+H: Show conversation history
        Ctrl+O: Save current conversation
        F1: Show this help information
        
        Type :quit to exit the application
        """

        self.chat_window.add_message(help_text, is_user=False)
        logger.debug("Help information displayed")
