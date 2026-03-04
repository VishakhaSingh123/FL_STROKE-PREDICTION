import hashlib
import json
import time

class Block:
    def __init__(self, index, event, data, previous_hash):
        self.index = index
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.event = event
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "event": self.event,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "event": self.event,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }


class BlockchainLogger:
    def __init__(self):
        self.chain = []
        # Create genesis block
        genesis = Block(0, "GENESIS", {"message": "FL Training Started"}, "0")
        self.chain.append(genesis)
        print(f"[BLOCKCHAIN] Genesis block created: {genesis.hash[:16]}...")

    def log(self, event, data):
        previous_block = self.chain[-1]
        new_block = Block(
            index=len(self.chain),
            event=event,
            data=data,
            previous_hash=previous_block.hash
        )
        self.chain.append(new_block)
        print(f"[BLOCKCHAIN] Block {new_block.index} logged | Event: {event} | Hash: {new_block.hash[:16]}...")
        return new_block

    def verify_chain(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            # Check hash integrity
            if current.hash != current.calculate_hash():
                print(f"[BLOCKCHAIN] ⚠️ Block {i} hash is invalid!")
                return False

            # Check chain linkage
            if current.previous_hash != previous.hash:
                print(f"[BLOCKCHAIN] ⚠️ Block {i} is not linked to previous block!")
                return False

        print("[BLOCKCHAIN] ✅ Chain verified — all blocks intact")
        return True

    def print_chain(self):
        print("\n========== BLOCKCHAIN AUDIT LOG ==========")
        for block in self.chain:
            print(json.dumps(block.to_dict(), indent=2))
            print("------------------------------------------")

    def save_chain(self, filename="audit_log.json"):
        with open(filename, "w") as f:
            json.dump([block.to_dict() for block in self.chain], f, indent=2)
        print(f"[BLOCKCHAIN] Audit log saved to {filename}")