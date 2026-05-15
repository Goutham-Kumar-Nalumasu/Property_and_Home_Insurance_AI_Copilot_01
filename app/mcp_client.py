import threading
import requests
import json
from typing import Dict, Any

class MCPClient:
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        self.base_url = base_url
        self._start_server_if_needed()

    def _start_server_if_needed(self):
        """Start the MCP server in a background thread if not already running."""
        try:
            requests.get(f"{self.base_url}/health", timeout=0.5)
        except:
            from app.mcp_server import mcp
            threading.Thread(target=mcp.run, daemon=True).start()
            import time
            time.sleep(1)  # wait for server to start

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Invoke an MCP tool via the /call endpoint (simplified)."""
        resp = requests.post(
            f"{self.base_url}/call",
            json={"tool": tool_name, "arguments": arguments},
            timeout=10
        )
        resp.raise_for_status()
        return resp.json().get("result", "")

mcp_client = MCPClient()