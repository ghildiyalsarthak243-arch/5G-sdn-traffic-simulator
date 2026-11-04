from collections import deque

from api_client import fetch_flow_records
from load_balancer import LoadBalancer
from qos_scheduler import QoSScheduler
from ringbuffer import RingBuffer
from trie import create_default_trie


class NetworkSimulation:
    """API ingestion and simulated packet-processing pipeline."""

    def __init__(self, buffer_capacity=10):
        self.trie = create_default_trie()
        self.buffer = RingBuffer(buffer_capacity)
        self.backlog = deque()
        self.load_balancer = LoadBalancer()
        self.scheduler = QoSScheduler()
        self.packets = []
        self.processed = []
        self.activity = ["Ready. Fetch recorded network-flow rows from the API."]
        self.api_offset = 0
        self.api_total_rows = None
        self.raw_rows_received = 0

    def _log(self, message):
        self.activity.insert(0, message)
        self.activity = self.activity[:100]

    def _classify(self, packet):
        packet.traffic_type, packet.priority = self.trie.classify(packet.destination_ip)

    def _fill_buffer_from_backlog(self):
        added = 0
        while self.backlog and not self.buffer.is_full():
            packet = self.backlog.popleft()
            packet.status = "In ring buffer"
            self.buffer.enqueue(packet)
            added += 1
        return added

    def fetch_from_api(self, count=25):
        packets, total_rows, raw_count = fetch_flow_records(self.api_offset, count)
        self.api_total_rows = total_rows
        self.api_offset += raw_count
        self.raw_rows_received += raw_count

        buffered = 0
        for packet in packets:
            self._classify(packet)
            self.packets.append(packet)
            if self.buffer.enqueue(packet):
                packet.status = "In ring buffer"
                buffered += 1
            else:
                packet.status = "Waiting in backlog"
                self.backlog.append(packet)

        self._log(
            f"API imported {len(packets)} valid flow record(s) from {raw_count} row(s). "
            f"{buffered} entered the ring buffer; {len(packets) - buffered} entered the backlog."
        )
        return {
            "imported": len(packets), "raw_rows": raw_count,
            "buffered": buffered, "backlogged": len(packets) - buffered,
            "offset": self.api_offset, "total": self.api_total_rows,
        }

    def dispatch(self):
        moved = 0
        self._fill_buffer_from_backlog()
        while not self.buffer.is_empty():
            packet = self.buffer.dequeue()
            self.load_balancer.assign(packet)
            self.scheduler.add(packet)
            moved += 1
            self._fill_buffer_from_backlog()
        self._log(f"Dispatched {moved} record(s) from buffer/backlog into the QoS Min-Heap.")
        return moved

    def process_next(self):
        if self.scheduler.is_empty() and (not self.buffer.is_empty() or self.backlog):
            self.dispatch()
        packet = self.scheduler.pop_next()
        if packet is None:
            return None
        packet.status = "Processed"
        self.load_balancer.mark_completed(packet)
        self.processed.append(packet)
        self._log(
            f"{packet.packet_id} processed on {packet.server}, priority {packet.priority}; "
            f"dataset label: {packet.dataset_label}."
        )
        return packet

    def process_all(self):
        self.dispatch()
        completed = []
        while not self.scheduler.is_empty():
            packet = self.process_next()
            if packet is not None:
                completed.append(packet)
        return completed

    def reset(self):
        self.__init__(self.buffer.capacity)

    def waiting_packets(self):
        return self.buffer.items()

    def backlog_packets(self):
        return list(self.backlog)

    def queued_packets(self):
        return self.scheduler.packets()

    def packet_rows(self):
        return [packet.to_dict() for packet in self.packets]

    @property
    def has_more_api_rows(self):
        return self.api_total_rows is None or self.api_offset < self.api_total_rows
