import time
from contextlib import contextmanager


@contextmanager
def timed_step(debug_trace: list[str], name: str):
    start = time.perf_counter()

    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        debug_trace.append(f"{name}:duration={elapsed:.2f}s")
