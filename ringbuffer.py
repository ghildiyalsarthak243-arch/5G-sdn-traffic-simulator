class RingBuffer:
    """Fixed-capacity FIFO circular buffer."""
    def __init__(self, capacity=10):
        if capacity < 1: raise ValueError("Capacity must be at least 1.")
        self.capacity = capacity
        self._items = [None] * capacity
        self.front = self.rear = self.size = 0
    def __len__(self): return self.size
    def is_empty(self): return self.size == 0
    def is_full(self): return self.size == self.capacity
    def enqueue(self, item):
        if self.is_full(): return False
        self._items[self.rear] = item
        self.rear = (self.rear + 1) % self.capacity
        self.size += 1
        return True
    def dequeue(self):
        if self.is_empty(): return None
        item = self._items[self.front]
        self._items[self.front] = None
        self.front = (self.front + 1) % self.capacity
        self.size -= 1
        return item
    def items(self): return [self._items[(self.front+i) % self.capacity] for i in range(self.size)]
    def clear(self):
        self._items = [None] * self.capacity
        self.front = self.rear = self.size = 0
