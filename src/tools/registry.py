"""Tool registry for managing available tools."""

from typing import Dict, Type, Optional
from .base import Tool, ToolConfig


class ToolRegistry:
    """Registry for managing available tools."""

    def __init__(self):
        """Initialize tool registry."""
        self._tools: Dict[str, Type[Tool]] = {}
        self._instances: Dict[str, Tool] = {}

    def register(self, tool_class: Type[Tool], name: str = None):
        """Register a tool class.

        Args:
            tool_class: Tool class to register
            name: Optional custom name (uses class name if not provided)
        """
        tool_name = name or tool_class.__name__
        self._tools[tool_name] = tool_class

    def get(self, name: str, config: ToolConfig = None) -> Optional[Tool]:
        """Get a tool instance.

        Args:
            name: Tool name
            config: Tool configuration (creates new instance if provided)

        Returns:
            Tool instance or None if not found
        """
        if config:
            # Create new instance with config
            if name in self._tools:
                return self._tools[name](config)
            return None

        # Return cached instance or create new one with default config
        if name not in self._instances:
            if name in self._tools:
                default_config = ToolConfig(name=name, description="")
                self._instances[name] = self._tools[name](default_config)
            else:
                return None

        return self._instances[name]

    def list_tools(self) -> list[str]:
        """List all registered tools.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def unregister(self, name: str):
        """Unregister a tool.

        Args:
            name: Tool name to unregister
        """
        if name in self._tools:
            del self._tools[name]
        if name in self._instances:
            del self._instances[name]


# Global registry instance
_global_registry = ToolRegistry()


def register_tool(tool_class: Type[Tool], name: str = None):
    """Register a tool in the global registry.

    Args:
        tool_class: Tool class to register
        name: Optional custom name
    """
    _global_registry.register(tool_class, name)


def get_tool(name: str, config: ToolConfig = None) -> Optional[Tool]:
    """Get a tool from the global registry.

    Args:
        name: Tool name
        config: Tool configuration

    Returns:
        Tool instance or None
    """
    return _global_registry.get(name, config)


def list_tools() -> list[str]:
    """List all registered tools.

    Returns:
        List of tool names
    """
    return _global_registry.list_tools()





