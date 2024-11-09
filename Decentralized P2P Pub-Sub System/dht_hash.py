import hashlib
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def hash_topic(topic):
    """Hashes a topic to a binary string suitable for hypercube addressing."""
    hash_value = int(hashlib.sha256(topic.encode()).hexdigest(), 16)
    binary_id = format(hash_value % 8, '03b')  # Mod 8 to ensure 3-bit binary ID
    logging.info(f"[DHT Hash] Topic '{topic}' hashed to ID '{binary_id}'")
    return binary_id
