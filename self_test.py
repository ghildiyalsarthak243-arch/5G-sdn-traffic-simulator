"""Offline checks for the packet conversion and data-structure pipeline."""
from api_client import flow_record_to_packet
from simulation import NetworkSimulation
from trie import create_default_trie

SAMPLE_ROWS = [
    {
        "Source IP": "205.174.165.73", "Destination IP": "192.168.10.50",
        "Label": "PortScan", "Destination Port": 80, "Flow Duration": 41000,
        "Total Fwd Packets": 2, "Total Backward Packets": 1,
        "Packet Length Mean": 64.5, "Flow Packets/s": 50.0,
    },
    {
        "Source IP": "192.168.10.50", "Destination IP": "8.8.8.8",
        "Label": "BENIGN", "Destination Port": 443, "Flow Duration": 1000,
        "Total Fwd Packets": 4, "Total Backward Packets": 3,
        "Packet Length Mean": 128.0, "Flow Packets/s": 70.0,
    },
]


def run_tests():
    trie = create_default_trie()
    assert trie.classify("10.2.3.4") == ("Emergency", 1)
    assert trie.classify("205.174.165.73") == ("High Data", 2)
    assert trie.classify("192.168.10.50") == ("Smart Devices", 3)
    assert trie.classify("8.8.8.8") == ("Normal", 4)

    first = flow_record_to_packet(SAMPLE_ROWS[0], 0, 1)
    second = flow_record_to_packet(SAMPLE_ROWS[1], 1, 2)
    assert first and second
    assert first.dataset_label == "PortScan"
    assert first.destination_ip == "192.168.10.50"
    assert flow_record_to_packet({"Source IP": "bad", "Destination IP": "1.1.1.1"}, 3, 4) is None

    sim = NetworkSimulation()
    # Simulate 26 validated API records without making a network request.
    for index in range(26):
        source = SAMPLE_ROWS[index % 2]
        packet = flow_record_to_packet(source, index, index + 1)
        sim._classify(packet)
        sim.packets.append(packet)
        if sim.buffer.enqueue(packet):
            packet.status = "In ring buffer"
        else:
            packet.status = "Waiting in backlog"
            sim.backlog.append(packet)

    assert len(sim.buffer) == 10
    assert len(sim.backlog) == 16
    assert sim.dispatch() == 26
    assert len(sim.scheduler) == 26
    completed = sim.process_all()
    assert len(completed) == 26
    assert len(sim.processed) == 26
    assert [item.priority for item in completed] == sorted(item.priority for item in completed)
    assert all(load == 0 for load in sim.load_balancer.server_loads.values())
    print("PASS: Trie prefix classification")
    print("PASS: API row conversion and IPv4 validation")
    print("PASS: 10-slot ring buffer + 16-record overflow backlog")
    print("PASS: Dispatch + Min-Heap priority processing")
    print("PASS: Server workloads return to zero")
    print("Note: this is an offline self-test; live API access is tested when the app fetches data.")


if __name__ == "__main__":
    run_tests()
