#!/usr/bin/env python3
import asyncio
import os
from typing import Dict, Any

import logging
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Static
from textual.reactive import reactive

from .api_client import SpyAPIClient
from .ui_manager import UIManager
from .conversation_manager import ConversationManager
from .websocket_manager import WebSocketManager
from .event_handler import EventHandler
from . import config as config

# Initialize logging
log_file = os.path.join(config.DATA_DIR, "spy_cli_debug.log")
logging.basicConfig(
    level=logging.DEBUG,  # Force DEBUG level for troubleshooting
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler(log_file)],
)
logger = logging.getLogger(config.APP_NAME)
logger.debug(f"Logging initialized. Log file: {log_file}")
logger.debug(f"API Base URL: {config.API_BASE_URL}")
logger.debug(f"WebSocket URL: {config.WS_BASE_URL}")


class SpyCommandConsole(App):
    """A terminal-based interface for interacting with AI-powered spy agents."""

    # Define keyboard bindings
    BINDINGS = [
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+s", "submit_message", "Send Message"),
        ("ctrl+c", "clear_input", "Clear Input"),
        ("ctrl+h", "show_history", "History"),
        ("ctrl+o", "save_conversation", "Save"),
        ("f1", "show_help", "Help"),
    ]

    CSS = """
    Screen {
        background: #000000;
        color: #00ff00;
    }
    
    .section-title {
        background: #003300;
        color: #00ff00;
        padding: 1;
        text-align: center;
        width: 100%;
    }
    
    .spy-name {
        background: #003300;
        color: #00ff00;
        width: 100%;
        text-align: left;
        padding: 0 1;
    }
    
    .spy-name.selected {
        background: #00aa00;
        color: #000000;
        text-style: bold;
    }
    
    #spy-selector {
        height: auto;
        margin: 1 0;
        border: solid green;
    }
    
    .spy-list {
        height: auto;
        border: none;
    }
    
    .spy-avatar {
        background: #003300;
        color: white;
        min-width: 4;
        text-align: center;
        margin-right: 1;
    }
    
    .spy-name {
        color: #00ff00;
    }
    
    #chat-container {
        height: 1fr;
        border: solid green;
        overflow-y: auto;
    }
    
    #input-container {
        height: 3;
        margin-top: 1;
        display: none;  /* Start hidden */
    }
    
    #input-container.visible {
        display: block;  /* Show when visible class is added */
    }
    
    #message-input {
        background: #111111;
        color: white;
        border: solid green;
        min-width: 60;
    }
    
    #send-button {
        background: #003300;
        color: #00ff00;
        min-width: 10;
    }
    
    #mode-selector {
        margin: 1 0;
        border: solid green;
        padding: 1;
    }
    
    .mode-title {
        color: #00ff00;
        margin-right: 2;
    }
    
    #mission-input {
        background: #111111;
        color: white;
        border: solid green;
        display: none;
    }
    
    #mission-input.visible {
        display: block;
    }
    
    .system-message {
        color: #ffff00;
        text-align: center;
    }
    
    .error-message {
        color: #ff0000;
        text-align: center;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
        ("enter", "select_focused_spy", "Select focused spy"),
    ]

    # Reactive attributes
    selected_spy = reactive(None)
    conversation_id = reactive(None)

    def __init__(self):
        super().__init__()
        self.api_client = SpyAPIClient()
        self.spies = []

        # Initialize managers
        self.ui_manager = UIManager(self)
        self.conversation_manager = ConversationManager()
        self.websocket_manager = WebSocketManager(self.api_client, self.ui_manager)
        self.event_handler = EventHandler(
            self, self.ui_manager, self.conversation_manager, self.websocket_manager
        )

        logger.info("SpyCommandConsole initialized")

    def compose(self) -> ComposeResult:
        """Create the UI layout"""
        yield Header(show_clock=True)

        # Main container
        with Container(id="main-container"):
            # Initial loading message
            yield Static("Loading spy agents...", id="loading-message")

        yield Footer()

    async def on_mount(self) -> None:
        """Load data when the app starts"""
        # Fetch spy list from API
        logger.info("Application mounted, fetching spy list")
        try:
            self.spies = await self.api_client.get_spies()
            logger.info(f"Loaded {len(self.spies)} spy agents")
            await self.ui_manager.setup_initial_ui(self.spies)
        except Exception as e:
            error_msg = f"Error loading spy agents: {str(e)}"
            logger.error(error_msg, exc_info=True)
            self.query_one("#loading-message").update(error_msg)

    async def on_spy_selected(self, spy_data: Dict[str, Any]) -> None:
        """Handle spy selection - delegate to event handler"""
        await self.event_handler.handle_spy_selection(spy_data)

    async def on_message_submitted(self, message: str) -> None:
        """Handle message submission - delegate to event handler"""
        await self.event_handler.handle_message_submission(message)

    async def action_quit(self) -> None:
        """Quit the application"""
        logger.info("Shutting down application")
        # Close API client connections
        await self.api_client.close()
        self.exit()

    def action_select_focused_spy(self) -> None:
        """Select the currently focused spy - delegate to event handler"""
        self.event_handler.handle_focused_spy_selection()

    async def action_submit_message(self) -> None:
        """Submit the current message"""
        input_bar = self.ui_manager.get_input_bar()
        if input_bar and input_bar.value:
            logger.debug("Submitting message via keyboard shortcut")
            await self.on_message_submitted(input_bar.value)
            input_bar.value = ""

    def action_clear_input(self) -> None:
        """Clear the input field - delegate to event handler"""
        self.event_handler.handle_clear_input()

    def action_toggle_chat_mode(self) -> None:
        """This method is kept for key binding compatibility but does nothing"""
        self.event_handler.handle_toggle_chat_mode()

    def action_show_help(self) -> None:
        """Show help information - delegate to event handler"""
        self.event_handler.handle_show_help()

    def action_save_conversation(self) -> None:
        """Save the current conversation - delegate to event handler"""
        asyncio.create_task(self.event_handler.handle_save_conversation())

    async def action_show_history(self) -> None:
        """Show conversation history - delegate to event handler"""
        await self.event_handler.handle_show_history()


if __name__ == "__main__":
    app = SpyCommandConsole()
    app.run()
