import time


def with_retry(fn, attempts=3, backoff=0.5):
    for i in range(attempts):
        try:
            return fn()
        except Exception:
            time.sleep(backoff * 2 ** i)
    return fn()
