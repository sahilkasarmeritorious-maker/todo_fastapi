import time
import uuid
import logging
import json
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# --- Logger setup ---
# In production this would write to a file or send to a log service
# like Datadog, Sentry, AWS CloudWatch etc
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
logger = logging.getLogger(__name__)

# Any request slower than this will trigger a warning
SLOW_REQUEST_THRESHOLD_MS = 500


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every request and response.
    Tracks request ID, method, path, status, timing.
    Warns on slow requests.
    """
    async def dispatch(self, request: Request, call_next):

        # --- generate unique request ID ---
        # every request gets its own ID
        # if user reports a bug, they give you this ID
        # and you can find exactly what happened
        request_id = str(uuid.uuid4())[:8]

        # attach request_id to request state
        # so any route can access it via request.state.request_id
        request.state.request_id = request_id

        start_time = time.time()

        # --- log incoming request ---
        logger.info(
            f"[{request_id}] ▶ {request.method} {request.url.path} "
            f"| IP: {request.client.host} "
            f"| Agent: {request.headers.get('user-agent', 'unknown')[:50]}"
        )

        # --- run the actual route ---
        try:
            response = await call_next(request)
        except Exception as e:
            # if something completely unexpected crashes
            # middleware catches it here so app never dies
            logger.error(
                f"[{request_id}] ❌ UNHANDLED ERROR "
                f"{request.method} {request.url.path} | Error: {str(e)}"
            )
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "Internal server error",
                    "request_id": request_id  # send request_id to frontend
                }
            )

        # --- calculate time taken ---
        process_time = (time.time() - start_time) * 1000

        # --- warn if request was slow ---
        if process_time > SLOW_REQUEST_THRESHOLD_MS:
            logger.warning(
                f"[{request_id}] ⚠️  SLOW REQUEST "
                f"{request.method} {request.url.path} "
                f"| Time: {process_time:.2f}ms "
                f"| Threshold: {SLOW_REQUEST_THRESHOLD_MS}ms"
            )

        # --- pick the right log level based on status code ---
        # 2xx = success → INFO
        # 4xx = client error → WARNING
        # 5xx = server error → ERROR
        if response.status_code >= 500:
            log_fn = logger.error
            symbol = "XX"
        elif response.status_code >= 400:
            log_fn = logger.warning
            symbol = "!!"
        else:
            log_fn = logger.info
            symbol = ">>"

        log_fn(
            f"[{request_id}] {symbol} {request.method} {request.url.path} "
            f"| Status: {response.status_code} "
            f"| Time: {process_time:.2f}ms"
        )

        # --- add headers to response ---
        # frontend can read these for debugging
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Global error handler.
    Catches any unhandled exception in the entire app
    and returns a clean JSON response instead of
    crashing or returning an ugly HTML error page.
    """
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except ValueError as e:
            # validation type errors
            logger.warning(f"ValueError: {str(e)} | Path: {request.url.path}")
            return JSONResponse(
                status_code=422,
                content={
                    "success": False,
                    "message": str(e)
                }
            )
        except Exception as e:
            # anything else
            logger.error(
                f"Unhandled exception: {str(e)} "
                f"| Path: {request.url.path} "
                f"| Method: {request.method}"
            )
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "Something went wrong on our end. Please try again."
                }
            )