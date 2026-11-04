from dataclasses import dataclass


@dataclass
class Packet:
    """A dataset flow record wrapped as a packet work item for the simulator.

    CIC-IDS-2017 API rows describe recorded network flows, not individual
    live packets. The original dataset label is retained separately.
    """
    packet_id: str
    source_ip: str
    destination_ip: str
    traffic_type: str = "Unclassified"
    priority: int = 4
    dataset_label: str = "Unknown"
    destination_port: int = 0
    flow_duration: float = 0.0
    total_fwd_packets: int = 0
    total_backward_packets: int = 0
    packet_length_mean: float = 0.0
    flow_packets_per_second: float = 0.0
    server: str = "Unassigned"
    status: str = "Imported"
    arrival_order: int = 0

    @property
    def size_bytes(self) -> int:
        """Approximate mean packet length from the flow record."""
        return max(0, int(round(self.packet_length_mean)))

    def to_dict(self):
        return {
            "Record ID": self.packet_id,
            "Source IP": self.source_ip,
            "Destination IP": self.destination_ip,
            "Traffic Class (Trie)": self.traffic_type,
            "Priority": self.priority,
            "Original Dataset Label": self.dataset_label,
            "Destination Port": self.destination_port,
            "Mean Packet Length (bytes)": round(self.packet_length_mean, 2),
            "Flow Duration": round(self.flow_duration, 2),
            "Forward Packets": self.total_fwd_packets,
            "Backward Packets": self.total_backward_packets,
            "Flow Packets/s": round(self.flow_packets_per_second, 4),
            "Server": self.server,
            "Status": self.status,
        }
