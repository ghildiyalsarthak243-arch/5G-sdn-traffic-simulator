import heapq
import itertools


class QoSScheduler:
    """Min-Heap: lower numeric priority first; arrival order breaks ties."""

    def __init__(self):
        self._heap = []
        self._sequence = itertools.count()

    def __len__(self):
        return len(self._heap)

    def is_empty(self):
        return not self._heap

    def add(self, packet):
        heapq.heappush(
            self._heap,
            (packet.priority, packet.arrival_order, next(self._sequence), packet),
        )

    def pop_next(self):
        return heapq.heappop(self._heap)[3] if self._heap else None

    def packets(self):
        return [entry[3] for entry in sorted(self._heap, key=lambda entry: entry[:3])]

    def clear(self):
        self._heap.clear()
        self._sequence = itertools.count()
