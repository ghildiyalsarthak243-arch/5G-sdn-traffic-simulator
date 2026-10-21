class LoadBalancer:
    """Assign packets to the server with the least pending workload."""
    def __init__(self, server_names=None):
        self.server_loads = {name: 0 for name in (server_names or ["Server 1", "Server 2", "Server 3"])}
    def assign(self, packet):
        server = min(self.server_loads, key=self.server_loads.get)
        self.server_loads[server] += 1
        packet.server, packet.status = server, "Queued for processing"
        return server
    def mark_completed(self, packet):
        if packet.server in self.server_loads and self.server_loads[packet.server] > 0:
            self.server_loads[packet.server] -= 1
    def reset(self):
        for server in self.server_loads: self.server_loads[server] = 0
