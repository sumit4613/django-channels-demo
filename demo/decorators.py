import logging
from functools import wraps

import websockets

logger = logging.getLogger(__name__)


def handle_ws_disconnects(func):
    """
    Decorator which handles ws disconnects. Logs the exception and returns None.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, *kwargs)
        except websockets.ConnectionClosed as exc:
            logger.debug(
                f"Connection got closed during execution of {func.__name__}.",
                extra={"exception": str(exc)},
            )
    return wrapper
