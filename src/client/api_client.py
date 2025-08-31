import asyncio
import logging
from typing import Dict, List, Any, Optional

import httpx
import websockets

from . import config as config


class SpyAPIClient:
    """Client for interacting with the Spy API"""
    
    def __init__(self, base_url: str = config.API_BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=config.API_TIMEOUT)
        self.ws = None
        self.ws_connected = False
        self.reconnect_attempts = 0
        self.ws_retry_attempts = config.WS_RECONNECT_ATTEMPTS
        self.ws_retry_delay = config.WS_RECONNECT_DELAY
    
    async def get_spies(self) -> List[Dict[str, Any]]:
        """
        Get list of available spies
        
        Raises:
            httpx.HTTPStatusError: If the API returns an error status code
            httpx.RequestError: If the request fails to be sent
            ConnectionError: If the server is unreachable
        """
        try:
            logging.debug(f"Fetching spies from {self.base_url}/api/spies/")
            response = await self.client.get(f"{self.base_url}/api/spies/")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_msg = f"API Error: HTTP {e.response.status_code} - {e.response.text}"
            logging.error(error_msg)
            raise ConnectionError(error_msg)
        except httpx.RequestError as e:
            error_msg = f"Connection Error: Unable to reach {self.base_url}/api/spies/. Please check your network connection and ensure the server is running."
            logging.error(f"{error_msg} Details: {str(e)}")
            raise ConnectionError(error_msg)
    
    async def get_spy(self, spy_id: str) -> Dict[str, Any]:
        """
        Get details for a specific spy
        
        Raises:
            httpx.HTTPStatusError: If the API returns an error status code
            httpx.RequestError: If the request fails to be sent
            ConnectionError: If the server is unreachable
        """
        try:
            response = await self.client.get(f"{self.base_url}/api/spies/{spy_id}")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                error_msg = f"Spy not found: No spy exists with ID '{spy_id}'"
            else:
                error_msg = f"API Error: HTTP {e.response.status_code} - {e.response.text}"
            logging.error(error_msg)
            raise ConnectionError(error_msg)
        except httpx.RequestError as e:
            error_msg = f"Connection Error: Unable to reach {self.base_url}/api/spies/{spy_id}. Please check your network connection and ensure the server is running."
            logging.error(f"{error_msg} Details: {str(e)}")
            raise ConnectionError(error_msg)
    
    async def create_conversation(self, spy_id: str) -> Dict[str, Any]:
        """
        Create a new conversation
        
        Raises:
            httpx.HTTPStatusError: If the API returns an error status code
            httpx.RequestError: If the request fails to be sent
            ConnectionError: If the server is unreachable
        """
        try:
            # Using form data instead of JSON as per OpenAPI spec
            response = await self.client.post(
                f"{self.base_url}/api/conversations",
                data={"spy_id": spy_id}
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_msg = f"API Error: HTTP {e.response.status_code} - {e.response.text}"
            logging.error(error_msg)
            raise ConnectionError(error_msg)
        except httpx.RequestError as e:
            error_msg = f"Connection Error: Unable to reach {self.base_url}/api/conversations. Please check your network connection and ensure the server is running."
            logging.error(f"{error_msg} Details: {str(e)}")
            raise ConnectionError(error_msg)
    
    async def chat_with_history(
        self, 
        spy_id: str, 
        conversation_id: str, 
        message: str,
        tool_calls: Optional[List[Dict]] = None,
        tool_outputs: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Send a message with conversation history context and optional tool calls.
        
        Args:
            spy_id: ID of the spy to chat with
            conversation_id: ID of the conversation
            message: The message to send
            tool_calls: List of tool calls to process
            tool_outputs: Outputs from previous tool calls
            
        Returns:
            Dict containing the response and any tool calls
            
        Raises:
            httpx.HTTPStatusError: If the API returns an error status code
            httpx.RequestError: If the request fails to be sent
            ConnectionError: If the server is unreachable
        """
        try:
            payload = {"message": message}
            if tool_calls:
                payload["tool_calls"] = tool_calls
            if tool_outputs:
                payload["tool_outputs"] = tool_outputs
                
            response = await self.client.post(
                f"{self.base_url}/api/chat/conversation/{conversation_id}",
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                error_msg = f"Not found: Either spy '{spy_id}' or conversation '{conversation_id}' does not exist"
            elif e.response.status_code == 422:
                error_msg = f"Validation Error: The request format is invalid. Details: {e.response.text}"
            else:
                error_msg = f"API Error: HTTP {e.response.status_code} - {e.response.text}"
            logging.error(error_msg)
            raise ConnectionError(error_msg)
        except httpx.RequestError as e:
            error_msg = f"Connection Error: Unable to reach {self.base_url}/api/chat/conversation/{conversation_id}. Please check your network connection and ensure the server is running."
            logging.error(f"{error_msg} Details: {str(e)}")
            raise ConnectionError(error_msg)
    
    async def connect_websocket(self, spy_id: str, conversation_id: Optional[str] = None) -> websockets.WebSocketClientProtocol:
        """
        Connect to the WebSocket for real-time chat updates with auto-reconnect.
        
        Args:
            spy_id: ID of the spy to chat with
            conversation_id: Optional conversation ID for continuing a conversation
            
        Returns:
            WebSocket client connection
            
        Raises:
            ConnectionError: If WebSocket connection fails after retries
        """
        # Use the configured WebSocket base URL
        if conversation_id:
            ws_url = f"{config.WS_BASE_URL}/ws/chat/{spy_id}/conversation/{conversation_id}"
        else:
            ws_url = f"{config.WS_BASE_URL}/ws/chat/{spy_id}"
        
        logging.info(f"Connecting to WebSocket: {ws_url}")
        
        # Implement reconnection logic with exponential backoff
        for attempt in range(self.ws_retry_attempts):
            try:
                if attempt > 0:
                    backoff = min(self.ws_retry_delay * (2 ** (attempt - 1)), 30)  # Cap at 30 seconds
                    logging.info(f"Reconnection attempt {attempt+1}/{self.ws_retry_attempts} in {backoff}s")
                    await asyncio.sleep(backoff)
                
                # Add timeout to the WebSocket connection
                self.ws = await asyncio.wait_for(
                    websockets.connect(ws_url),
                    timeout=10.0  # 10 second timeout for connection
                )
                
                # Verify connection is alive
                await asyncio.wait_for(self.ws.ping(), timeout=5.0)
                
                self.ws_connected = True
                self.reconnect_attempts = 0
                logging.info("WebSocket connection established")
                return self.ws
                
            except asyncio.TimeoutError:
                error_msg = f"WebSocket connection timed out (attempt {attempt+1}/{self.ws_retry_attempts})"
                logging.error(error_msg)
                if attempt == self.ws_retry_attempts - 1:  # Last attempt
                    raise ConnectionError(f"WebSocket connection failed: {error_msg}. Please check your network connection and ensure the server is running.")
                    
            except Exception as e:
                self.reconnect_attempts += 1
                error_msg = f"WebSocket connection failed (attempt {attempt+1}/{self.ws_retry_attempts}): {str(e)}"
                logging.error(error_msg, exc_info=True)
                
                if attempt == self.ws_retry_attempts - 1:  # Last attempt
                    raise ConnectionError(f"WebSocket connection failed after {self.ws_retry_attempts} attempts: {str(e)}. Please check your network connection and ensure the server is running.")
                
        # This should theoretically never be reached due to the raise statements above
        raise ConnectionError("Unexpected error in WebSocket connection")
    
    async def close(self):
        """Close all connections"""
        logging.debug("Closing API client connections")
        if self.ws and not self.ws.closed:
            await self.ws.close()
            self.ws_connected = False
        await self.client.aclose()
