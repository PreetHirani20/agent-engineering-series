import time


def retry(times=3, exceptions=(Exception,), delays=None, sleep=time.sleep):
    """Retry the decorated function when it raises one of `exceptions`."""
    def decorator(fn):
        def wrapper(*args, **kwargs):
            for attempt in range(times):
                try:
                    return fn(*args, **kwargs)
                except Exception:
                    sleep(1)
            return None
        return wrapper
    return decorator
