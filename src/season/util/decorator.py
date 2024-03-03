import time

class decorator:
    @staticmethod
    def timer(func):
        def fn(*args, **kwargs):
            st = round(time.time() * 1000)
            func(*args, **kwargs)
            et = round(time.time() * 1000)
            print(f"[timelab]", et - st, "ms")
        return fn
