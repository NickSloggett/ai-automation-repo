"""Tools system for AI automation."""

from .base import Tool, ToolResult, ToolConfig
from .registry import ToolRegistry, register_tool, get_tool
from .web_scraper import WebScraperTool
from .email_tool import EmailTool
from .api_tool import APITool
from .data_processor import DataProcessorTool

__all__ = [
    "Tool",
    "ToolResult",
    "ToolConfig",
    "ToolRegistry",
    "register_tool",
    "get_tool",
    "WebScraperTool",
    "EmailTool",
    "APITool",
    "DataProcessorTool",
]





