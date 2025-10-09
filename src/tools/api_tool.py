"""API integration tool."""

from typing import Dict, Optional, Any
import httpx
import structlog

from .base import Tool, ToolResult, ToolConfig

logger = structlog.get_logger(__name__)


class APITool(Tool):
    """Tool for making API requests."""

    def __init__(self, config: ToolConfig):
        """Initialize API tool.

        Args:
            config: Tool configuration
        """
        super().__init__(config)
        self.logger = logger.bind(tool="api")

    async def execute(
        self,
        url: str,
        method: str = "GET",
        headers: Dict[str, str] = None,
        params: Dict[str, Any] = None,
        json: Dict[str, Any] = None,
        data: Dict[str, Any] = None,
        timeout: int = 30,
        auth: tuple = None,
    ) -> ToolResult:
        """Make an API request.

        Args:
            url: API endpoint URL
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            headers: Request headers
            params: Query parameters
            json: JSON body
            data: Form data
            timeout: Request timeout in seconds
            auth: Basic auth tuple (username, password)

        Returns:
            API response
        """
        try:
            self.logger.info("Making API request", url=url, method=method)

            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method.upper(),
                    url=url,
                    headers=headers,
                    params=params,
                    json=json,
                    data=data,
                    timeout=timeout,
                    auth=auth,
                )

                # Try to parse JSON response
                try:
                    response_data = response.json()
                except Exception:
                    response_data = response.text

                result_data = {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'data': response_data,
                    'url': str(response.url),
                }

                # Check if request was successful
                if response.is_success:
                    self.logger.info(
                        "API request successful",
                        url=url,
                        status_code=response.status_code,
                    )
                    return ToolResult(
                        success=True,
                        data=result_data,
                        metadata={'method': method, 'status_code': response.status_code},
                    )
                else:
                    self.logger.warning(
                        "API request failed",
                        url=url,
                        status_code=response.status_code,
                    )
                    return ToolResult(
                        success=False,
                        error=f"API request failed with status {response.status_code}",
                        data=result_data,
                    )

        except Exception as e:
            self.logger.error("API request error", url=url, error=str(e))
            return ToolResult(
                success=False,
                error=f"API request error: {str(e)}",
            )





