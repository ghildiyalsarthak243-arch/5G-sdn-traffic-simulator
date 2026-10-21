import random
from packet import Packet

SOURCE_PREFIXES = ["192.0.2", "203.0.113"]
DESTINATION_POOLS = {
    "Emergency": "10.10.0",
    "High Data": "172.16.1",
    "Smart Devices": "10.20.0",
    "Normal": "198.51.100",
}

def generate_packet(packet_number: int) -> Packet:
    traffic_type = random.choices(list(DESTINATION_POOLS), weights=[10, 30, 30, 30], k=1)[0]
    return Packet(packet_id=f"P{packet_number:03}", source_ip=f"{random.choice(SOURCE_PREFIXES)}.{random.randint(1,254)}", destination_ip=f"{DESTINATION_POOLS[traffic_type]}.{random.randint(1,254)}", size_bytes=random.randint(64,1500), arrival_order=packet_number)

def generate_packets(count: int, start_id: int = 1) -> list[Packet]:
    if count < 0: raise ValueError("Packet count cannot be negative.")
    return [generate_packet(n) for n in range(start_id, start_id+count)]
