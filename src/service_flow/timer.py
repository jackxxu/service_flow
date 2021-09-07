from time import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def measure_timing(func):
    @wraps(func)
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        logger.info(f'stack execution completes in {(t2-t1):.4f}s')
        return result
    return wrap_func
