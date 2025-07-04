import bisect
import hashlib

class ConsistentHash:
    def __init__(self, num_servers, num_slots=512, virtuals_per_server=9):
        self.num_slots = num_slots
        self.virtuals = virtuals_per_server
        self.servers = {}  # key: slot index, value: server_id
        self.slots = []    # sorted list of all slot indexes

        self.server_ids = [i + 1 for i in range(num_servers)]
        for sid in self.server_ids:
            self._add_virtual_servers(sid)

    def _hash_request(self, req_id):
        hash_val = hashlib.sha256(str(req_id).encode()).hexdigest()
        return int(hash_val, 16) % self.num_slots

    def _hash_virtual(self, server_id, replica_id):
        # Add entropy for better distribution
        key = f"virtual-{server_id}-replica-{replica_id}-salt42"
        hash_val = hashlib.md5(key.encode()).hexdigest()
        return int(hash_val, 16) % self.num_slots

    def _add_virtual_servers(self, server_id):
        for j in range(self.virtuals):
            slot = self._hash_virtual(server_id, j)
            i = 1  # for quadratic probing
            while slot in self.servers:
                slot = (slot + i**2) % self.num_slots
                i += 1
            self.servers[slot] = server_id
            bisect.insort(self.slots, slot)

    def get_server_for_request(self, req_id):
        slot = self._hash_request(req_id)
        index = bisect.bisect_left(self.slots, slot)
        if index == len(self.slots):
            index = 0  # wrap around
        mapped_slot = self.slots[index]
        server_id = self.servers[mapped_slot]
        return f"server{server_id}"

    def print_ring(self):
        for slot in self.slots:
            print(f"Slot {slot} -> Server {self.servers[slot]}")
