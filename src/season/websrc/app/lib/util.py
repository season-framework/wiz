import time
import string
import random

def randomstring(length=12):
    string_pool = string.ascii_letters + string.digits
    result = ""
    for i in range(length):
        result += random.choice(string_pool)
    return result.lower()

class Timelab:

    def __init__(self):
        self.timestamp = None

    def timelab(self, tag=None):
        newtime = round(time.time() * 1000)
        if tag is not None and self.timestamp is not None:
            print(f"[timelab][{tag}]", newtime - self.timestamp, "ms")
        self.timestamp = newtime

timelab = Timelab().timelab