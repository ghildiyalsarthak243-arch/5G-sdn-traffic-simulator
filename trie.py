import ipaddress

class TrieNode:
    def __init__(self):
        self.children = {"0": None, "1": None}
        self.traffic_type = None
        self.priority = None

class IPTrie:
    """Bitwise IPv4 prefix trie with longest-prefix matching."""
    def __init__(self, default_type="Normal", default_priority=4):
        self.root = TrieNode()
        self.default = (default_type, default_priority)

    def insert(self, network, traffic_type, priority):
        net = ipaddress.IPv4Network(network, strict=False)
        node = self.root
        bits = f"{int(net.network_address):032b}"
        for bit in bits[:net.prefixlen]:
            if node.children[bit] is None: node.children[bit] = TrieNode()
            node = node.children[bit]
        node.traffic_type, node.priority = traffic_type, priority

    def classify(self, ip_address):
        bits = f"{int(ipaddress.IPv4Address(ip_address)):032b}"
        node, best = self.root, self.default
        if node.traffic_type is not None: best = (node.traffic_type, node.priority)
        for bit in bits:
            node = node.children[bit]
            if node is None: break
            if node.traffic_type is not None: best = (node.traffic_type, node.priority)
        return best

def create_default_trie():
    trie = IPTrie()
    trie.insert("10.0.0.0/8", "Smart Devices", 3)
    trie.insert("10.10.0.0/16", "Emergency", 1)
    trie.insert("172.16.0.0/12", "High Data", 2)
    trie.insert("198.51.100.0/24", "Normal", 4)
    return trie
