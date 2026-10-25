import functools
import time


def retry(times=3, exceptions=(Exception,), delays=None, sleep=time.sleep):
    """Retry the decorated function when it raises one of `exceptions`."""
    if times < 1:
        raise ValueError("times must be at least 1")

    def delay_for(retry_number):
        if not delays:
            return 1
        return delays[min(retry_number, len(delays) - 1)]

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except exceptions:
                    if attempt == times - 1:
                        raise
                    sleep(delay_for(attempt))
        return wrapper
    return decorator
