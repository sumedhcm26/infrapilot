"""
Request Logging Middleware
==========================
Middleware intercepts every HTTP request/response.
This logs the method, path, status code, and processing time for every request.

This is similar to nginx/Apache access logs, but at the application layer.
In production, these logs would be sent to a log aggregation service.
"""

import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("infrapilot.requests")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Log every incoming HTTP request with timing information.

    Format: METHOD /path -> STATUS_CODE (XXXms)
    Example: GET /api/v1/services -> 200 (12.3ms)
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()

        # Process the request through the rest of the app
        response = await call_next(request)

        # Calculate how long it took
        process_time_ms = (time.time() - start_time) * 1000

        # Log it
        logger.info(
            f"{request.method} {request.url.path} -> {response.status_code} "
            f"({process_time_ms:.1f}ms)"
        )

        # Add timing header to response (useful for debugging)
        response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.1f}"

        return response
