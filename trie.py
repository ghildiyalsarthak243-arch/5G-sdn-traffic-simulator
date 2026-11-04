import ipaddress


class TrieNode:
    def __init__(self):
        self.children = {"0": None, "1": None}
        self.traffic_type = None
        self.priority = None


class IPTrie:
    """Binary IPv4 prefix Trie supporting longest-prefix matching."""

    def __init__(self, default_type="Normal", default_priority=4):
        self.root = TrieNode()
        self.default = (default_type, default_priority)

    def insert(self, network, traffic_type, priority):
        network = ipaddress.IPv4Network(network, strict=False)
        node = self.root
        bits = f"{int(network.network_address):032b}"
        for bit in bits[:network.prefixlen]:
            if node.children[bit] is None:
                node.children[bit] = TrieNode()
            node = node.children[bit]
        node.traffic_type = traffic_type
        node.priority = int(priority)

    def classify(self, ip_address):
        address = ipaddress.IPv4Address(ip_address)
        bits = f"{int(address):032b}"
        node = self.root
        best = self.default
        for bit in bits:
            node = node.children[bit]
            if node is None:
                break
            if node.traffic_type is not None:
                best = (node.traffic_type, node.priority)
        return best


def create_default_trie():
    """Illustrative prefixes for the sample topology in the selected dataset.

    These are classroom traffic classes, not standardized 5G slice definitions.
    Edit the prefixes if an instructor supplies a different IP-to-class mapping.
    """
    trie = IPTrie(default_type="Normal", default_priority=4)
    trie.insert("10.0.0.0/8", "Emergency", 1)
    trie.insert("205.174.165.0/24", "High Data", 2)
    trie.insert("192.168.10.0/24", "Smart Devices", 3)
    return trie
