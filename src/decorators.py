import time
from datetime import datetime
from functools import wraps

def retry(max_tries, initial_wait=10, max_wait=90):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            tries = 0
            while tries < max_tries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    tries += 1
                    wait_time = min(max_wait, initial_wait * 2 ** tries)
                    print('=' * 10, datetime.now(), '=' * 10)
                    print(f'Error in {func.__name__}: {e}')
                    print(f'retrying ({tries}/{max_tries}) - waiting {wait_time} seconds')
                    if tries == max_tries:
                        print(f'failed to call {func.__name__}')
                        raise
                    else:
                        time.sleep(wait_time)
        return wrapper
    return decorator
