import heapq
import itertools

class QoSScheduler:
    """Min-Heap scheduler: priority 1 first, then arrival order."""
    def __init__(self):
        self._heap = []
        self._counter = itertools.count()
    def __len__(self): return len(self._heap)
    def is_empty(self): return not self._heap
    def add(self, packet):
        heapq.heappush(self._heap, (packet.priority, packet.arrival_order, next(self._counter), packet))
    def pop_next(self): return heapq.heappop(self._heap)[3] if self._heap else None
    def packets(self): return [entry[3] for entry in sorted(self._heap, key=lambda e: e[:3])]
    def clear(self):
        self._heap.clear()
        self._counter = itertools.count()
