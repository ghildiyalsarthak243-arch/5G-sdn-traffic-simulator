class LoadBalancer:
    """Least-loaded assignment across simulated servers."""

    def __init__(self, server_names=None):
        names = server_names or ["Server 1", "Server 2", "Server 3"]
        self.server_loads = {name: 0 for name in names}

    def assign(self, packet):
        server = min(self.server_loads, key=self.server_loads.get)
        self.server_loads[server] += 1
        packet.server = server
        packet.status = "Queued for processing"
        return server

    def mark_completed(self, packet):
        server = packet.server
        if server in self.server_loads and self.server_loads[server] > 0:
            self.server_loads[server] -= 1

    def reset(self):
        for server in self.server_loads:
            self.server_loads[server] = 0
