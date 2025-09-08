import logging

from uvicorn.config import LOGGING_CONFIG


LOG_CONFIG = LOGGING_CONFIG
LOG_CONFIG["formatters"]["access"]["fmt"] = (
    "%(levelprefix)s %(asctime)s - %(client_addr)s - %(request_line)s %(status_code)s"
)
LOG_CONFIG["formatters"]["default"]["fmt"] = "%(levelprefix)s %(asctime)s - %(message)s"


logging.config.dictConfig(LOG_CONFIG)
logger = logging.getLogger("logicore")
