import logging

logger = logging.getLogger(__name__)


def safe_call(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(e, stack_info=True)
            return None

    return wrapper
