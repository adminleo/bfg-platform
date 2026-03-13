"""BFG Core — Observability: structured logging and request correlation."""

from bfg_core.observability.logging import setup_logging, get_logger, RequestIdMiddleware

__all__ = ["setup_logging", "get_logger", "RequestIdMiddleware"]
