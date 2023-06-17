from loguru import logger

from ..env import PROJECT_DIR


def log_filter(data):
    exclude_keys = ("[REQUEST]", "[SMS]")
    for key in exclude_keys:
        if key in data["message"]:
            return None
    return data


logger.add(
    f"{PROJECT_DIR}/logs/exception.log",
    level="ERROR",
    enqueue=True,
    backtrace=True,
    diagnose=True,
)
logger.add(
    f"{PROJECT_DIR}/logs/info.log",
    level="INFO",
    filter=log_filter,
    enqueue=True,
    serialize=True,
)
logger.add(
    f"{PROJECT_DIR}/logs/request.log",
    level="INFO",
    filter=lambda x: "[REQUEST]" in x["message"],
    enqueue=True,
    serialize=True,
)
logger.add(
    f"{PROJECT_DIR}/logs/sms.log",
    level="INFO",
    filter=lambda x: "[SMS]" in x["message"],
    enqueue=True,
    serialize=True,
)
logger.add(
    f"{PROJECT_DIR}/logs/email.log",
    level="INFO",
    filter=lambda x: "[EMAIL]" in x["message"],
    enqueue=True,
    serialize=True,
)
