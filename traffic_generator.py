
import random
from packet import Packet


TRAFFIC_TYPES = {
    "Emergency": 1,
    "High Data": 2,
    "Smart Devices": 3,
    "Normal": 4,
}


def generate_packet(packet_number: int) -> Packet:
    traffic_type = random.choices(
        population=list(TRAFFIC_TYPES.keys()),
        weights=[10, 30, 30, 30],
        k=1,
    )[0]

    return Packet(
        packet_id=f"P{packet_number:03}",
        source_ip=f"192.0.2.{random.randint(1, 254)}",
        destination_ip=f"198.51.100.{random.randint(1, 254)}",
        traffic_type=traffic_type,
        priority=TRAFFIC_TYPES[traffic_type],
        size_bytes=random.randint(64, 1500),
    )


def generate_packets(count: int, start_id: int = 1) -> list[Packet]:
    if count < 0:
        raise ValueError("Packet count cannot be negative.")

    return [
        generate_packet(number)
        for number in range(start_id, start_id + count)
    ]