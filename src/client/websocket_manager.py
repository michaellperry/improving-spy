#!/usr/bin/env python3
"""WebSocket Manager for Spy CLI application."""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self, api_client, ui_manager):
        self.api_client = api_client
        self.ui_manager = ui_manager
        self.connected = False
        self.spy_id: Optional[str] = None
        self.conversation_id: Optional[str] = None

    async def connect(self, spy_id: str, conversation_id: str) -> None:
        """Connect to WebSocket for real-time updates."""
        try:
            if not spy_id:
                logger.warning("No spy ID provided, skipping WebSocket connection")
                return

            self.spy_id = spy_id
            self.conversation_id = conversation_id

            logger.info(f"Connecting to WebSocket for spy {spy_id}")

            # Update connection status
            self.ui_manager.update_connection_status("Connecting to WebSocket...")

            # Connect to WebSocket
            await self.api_client.connect_websocket(spy_id, conversation_id)

            # Update connection status
            self.ui_manager.update_connection_status("Connected (WebSocket)")
            self.connected = True

            logger.info("WebSocket connection established successfully")

        except Exception as e:
            logger.error(f"Error connecting to WebSocket: {str(e)}", exc_info=True)

            # Update connection status
            self.ui_manager.update_connection_status("WebSocket connection failed")
            self.connected = False

            # Show error in chat if available
            self.ui_manager.show_error(f"WebSocket connection failed: {str(e)}")

    async def disconnect(self) -> None:
        """Disconnect from WebSocket."""
        try:
            if self.connected:
                # Note: The API client should handle the actual disconnection
                self.connected = False
                self.spy_id = None
                self.conversation_id = None
                self.ui_manager.update_connection_status("Disconnected")
                logger.info("WebSocket disconnected")
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket: {str(e)}", exc_info=True)

    def is_connected(self) -> bool:
        """Check if WebSocket is connected."""
        return self.connected

    def get_connection_info(self) -> tuple[Optional[str], Optional[str]]:
        """Get current connection information."""
        return self.spy_id, self.conversation_id
