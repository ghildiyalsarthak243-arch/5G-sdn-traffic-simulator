
from dataclasses import dataclass


@dataclass
class Packet:
    packet_id: str
    source_ip: str
    destination_ip: str
    traffic_type: str = "Unclassified"
    priority: int = 4
    size_bytes: int = 0
    server: str = "Unassigned"
    status: str = "Waiting"

    def to_dict(self):
        return {
            "ID": self.packet_id,
            "Source IP": self.source_ip,
            "Destination IP": self.destination_ip,
            "Type": self.traffic_type,
            "Priority": self.priority,
            "Size (bytes)": self.size_bytes,
            "Server": self.server,
            "Status": self.status,
        }