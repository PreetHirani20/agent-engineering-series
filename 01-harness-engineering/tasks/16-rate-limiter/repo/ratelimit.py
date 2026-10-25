import time


class TokenBucket:
    def __init__(self, rate, capacity, clock=time.monotonic):
        self.rate = rate  # tokens per second
        self.capacity = capacity
        self.clock = clock
        self.tokens = 0
        self.last = clock()

    def _refill(self):
        now = self.clock()
        elapsed = int(now - self.last)
        self.tokens += elapsed * self.rate
        self.last = now

    def allow(self, cost=1):
        self._refill()
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False
