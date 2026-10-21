from traffic_generator import generate_packets
from trie import create_default_trie
from ringbuffer import RingBuffer
from load_balancer import LoadBalancer
from qos_scheduler import QoSScheduler


class NetworkSimulation:
    """Coordinate packet generation, classification, buffering, balancing, and scheduling.

    The ring buffer remains fixed-capacity. Packets that do not fit are preserved in
    a FIFO backlog and moved into the buffer automatically when slots become free.
    This is an educational simulation and does not send real network traffic.
    """

    def __init__(self, buffer_capacity=10):
        self.trie = create_default_trie()
        self.buffer = RingBuffer(buffer_capacity)
        self.load_balancer = LoadBalancer()
        self.scheduler = QoSScheduler()
        self.packets = []
        self.processed = []
        self.backlog = []
        self.activity = ["Simulation initialized."]
        self.next_packet_id = 1

    def _log(self, message):
        self.activity.insert(0, message)
        self.activity = self.activity[:100]

    def _refill_buffer(self):
        """Fill empty ring-buffer slots from the oldest packets in the backlog."""
        moved = 0
        while self.backlog and not self.buffer.is_full():
            packet = self.backlog.pop(0)
            # enqueue should succeed because we check is_full above.
            if self.buffer.enqueue(packet):
                packet.status = "In ring buffer"
                moved += 1
                self._log(f"{packet.packet_id}: moved from backlog into ring buffer.")
            else:
                # Defensive recovery: never lose the packet if buffer behavior changes.
                self.backlog.insert(0, packet)
                packet.status = "Waiting in backlog"
                break
        return moved

    def generate(self, count):
        """Generate count packets; overflow is retained in a FIFO backlog.

        Returns (number of newly generated packets now in the buffer,
        number of newly generated packets still waiting in the backlog).
        """
        if count < 0:
            raise ValueError("Packet count cannot be negative.")

        generated = generate_packets(count, self.next_packet_id)
        self.next_packet_id += count

        for packet in generated:
            packet.traffic_type, packet.priority = self.trie.classify(packet.destination_ip)
            packet.status = "Waiting in backlog"
            self.packets.append(packet)
            self.backlog.append(packet)
            self._log(
                f"{packet.packet_id}: classified as {packet.traffic_type}; added to incoming backlog."
            )

        self._refill_buffer()
        in_buffer_ids = {id(packet) for packet in self.buffer.items()}
        newly_buffered = sum(id(packet) in in_buffer_ids for packet in generated)
        still_backlogged = len(generated) - newly_buffered
        if still_backlogged:
            self._log(f"Buffer capacity reached; {still_backlogged} new packet(s) safely queued in backlog.")
        return newly_buffered, still_backlogged

    def dispatch(self):
        """Dispatch the current buffer batch, then refill it from the backlog.

        Only packets present in the ring buffer at the start of this call are
        dispatched. That keeps the buffer capacity meaningful and makes each batch
        visible in the UI. Slots freed by dispatch are then filled from the backlog.
        """
        batch_size = len(self.buffer)
        moved = 0
        for _ in range(batch_size):
            packet = self.buffer.dequeue()
            if packet is None:
                break
            self.load_balancer.assign(packet)
            self.scheduler.add(packet)
            moved += 1
            self._log(
                f"{packet.packet_id}: assigned to {packet.server} and added to QoS heap."
            )

        refilled = self._refill_buffer()
        if refilled:
            self._log(f"Ring buffer refilled with {refilled} packet(s) from backlog.")
        return moved

    def dispatch_all(self):
        """Dispatch every buffered/backlogged packet into the QoS heap in batches."""
        total = 0
        while not self.buffer.is_empty() or self.backlog:
            if self.buffer.is_empty():
                self._refill_buffer()
            if self.buffer.is_empty():
                break
            total += self.dispatch()
        return total

    def process_next(self):
        packet = self.scheduler.pop_next()
        if packet is None:
            return None
        packet.status = "Processed"
        self.load_balancer.mark_completed(packet)
        self.processed.append(packet)
        self._log(
            f"{packet.packet_id}: processed on {packet.server} (priority {packet.priority})."
        )
        return packet

    def process_all(self):
        done = []
        while not self.scheduler.is_empty():
            packet = self.process_next()
            if packet is not None:
                done.append(packet)
        return done

    def process_all_pending(self):
        """Dispatch every pending batch before processing by global priority."""
        dispatched = self.dispatch_all()
        processed = self.process_all()
        return dispatched, processed

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
