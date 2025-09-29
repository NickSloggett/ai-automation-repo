"""AI Automation Boilerplate - Core Package."""

from .agents import BaseAgent, TaskAgent, DecisionAgent
from .config import get_settings
from .database import get_database_session
from .logging import get_logger, setup_logging
from .monitoring import init_monitoring, track_performance
from .vector_store import get_vector_store

__version__ = "0.1.0"
__all__ = [
    "BaseAgent",
    "TaskAgent",
    "DecisionAgent",
    "get_settings",
    "get_database_session",
    "get_logger",
    "setup_logging",
    "init_monitoring",
    "track_performance",
    "get_vector_store",
]
