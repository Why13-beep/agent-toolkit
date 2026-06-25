# tools/base_tool.py
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class BaseTool:
    """Class dasar semua tools"""

    def __init__(self):
        self.logger = logger

    
    def _log_request(self, url: str, params: Optional[dict] = None):
        """Log request ke external API (opsional)."""
        self.logger.info(f"Requesting {url} with params: {params}")    

    def _log_error(self, error_msg: str):
        """Log error."""
        self.logger.error(error_msg)

    def _handle_request_exception(self, e: Exception, service_name: str):
        """Handle exception umum dari request."""
        error_msg = f"[{service_name} Error] Request failed: {e}"
        self._log_error(error_msg)
        # Bisa return pesan error atau raise custom exception
        return {"error": error_msg}