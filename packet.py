from dataclasses import dataclass, asdict

@dataclass
class Packet:
    packet_id: str
    source_ip: str
    destination_ip: str
    traffic_type: str = "Unclassified"
    priority: int = 4
    size_bytes: int = 0
    server: str = "Unassigned"
    status: str = "Generated"
    arrival_order: int = 0

    def to_dict(self):
        d = asdict(self)
        return {"ID": d["packet_id"], "Source IP": d["source_ip"], "Destination IP": d["destination_ip"], "Type": d["traffic_type"], "Priority": d["priority"], "Size (bytes)": d["size_bytes"], "Server": d["server"], "Status": d["status"]}
