import time


class TokenBucket:
    def __init__(self, rate, capacity, clock=time.monotonic):
        if rate <= 0 or capacity <= 0:
            raise ValueError("rate and capacity must be positive")
        self.rate = rate  # tokens per second
        self.capacity = capacity
        self.clock = clock
        self.tokens = float(capacity)
        self.last = clock()

    def _refill(self):
        now = self.clock()
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now

    def allow(self, cost=1):
        if cost <= 0 or cost > self.capacity:
            raise ValueError("cost must be between 1 and capacity")
        self._refill()
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False
