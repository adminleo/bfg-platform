"""Structured JSON logging with request-ID correlation.

Usage in product main.py:
    from bfg_core.observability import setup_logging, get_logger, RequestIdMiddleware

    setup_logging(log_level="INFO", json_format=True)
    app.add_middleware(RequestIdMiddleware)

    logger = get_logger(__name__)
    logger.info("server_started", port=8000)
"""

import logging
import sys
import uuid
from contextvars import ContextVar

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Context var for request-scoped data
_request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def _add_request_id(
    logger: logging.Logger,
    method_name: str,
    event_dict: dict,
) -> dict:
    """Structlog processor: inject current request_id into every log line."""
    rid = _request_id_var.get()
    if rid:
        event_dict["request_id"] = rid
    return event_dict


def setup_logging(
    log_level: str = "INFO",
    json_format: bool = True,
) -> None:
    """Configure structlog for the entire process.

    Args:
        log_level: Python log level name (DEBUG, INFO, WARNING, ERROR).
        json_format: True for JSON output (production), False for colored console (dev).
    """
    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        _add_request_id,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if json_format:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Quiet noisy libraries
    for lib in ("uvicorn.access", "httpx", "httpcore", "aioboto3", "botocore"):
        logging.getLogger(lib).setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a named structlog logger."""
    return structlog.get_logger(name)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """FastAPI/Starlette middleware that propagates X-Request-ID.

    - Reads X-Request-ID from incoming request header (or generates a UUID4).
    - Stores it in a context var so every log line includes it.
    - Sets X-Request-ID on the response header.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        token = _request_id_var.set(request_id)
        try:
            response: Response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            _request_id_var.reset(token)
