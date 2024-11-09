import hashlib
import time
import asyncio
import os
import sys
import uuid
import subprocess
import matplotlib.pyplot as plt

# Ensure the tests can find the client API and other project files
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from client_api import ClientAPI

def start_peer_node(node_id):
    """Start a peer node process with the given node ID."""
    return subprocess.Popen(
        [sys.executable, os.path.join(parent_dir, 'peer_node.py'), node_id],
        stdout=None,  # Redirect to None to avoid buffer issues
        stderr=None
    )

def hash_topic_md5(topic):
    """Hash topic using MD5 to generate a binary ID for DHT."""
    hash_value = int(hashlib.md5(topic.encode()).hexdigest(), 16)
    return format(hash_value % 8, '03b')  # 3-bit binary ID

def hash_topic_sha256(topic):
    """Hash topic using SHA-256 to generate a binary ID for DHT."""
    hash_value = int(hashlib.sha256(topic.encode()).hexdigest(), 16)
    return format(hash_value % 8, '03b')

async def setup_topics_with_hash_function(client_apis, hash_function, retries=3, delay=1):
    """Create topics on each peer using the specified hash function."""
    distribution = {client.node_id: 0 for client in client_apis}
    latencies = []

    for _ in range(100):  # Reduced to 100 for testing; increase as needed
        topic_name = f"topic_{uuid.uuid4()}"
        target_node = hash_function(topic_name)

        for attempt in range(retries):
            try:
                start_time = time.time()
                await asyncio.wait_for(client_apis[int(target_node, 2)].create_topic(topic_name), timeout=5)
                end_time = time.time()
                latencies.append(end_time - start_time)
                distribution[target_node] += 1
                break
            except asyncio.TimeoutError:
                print(f"[ERROR] Timeout on attempt {attempt + 1} for topic '{topic_name}' on node '{target_node}'")
                await asyncio.sleep(delay)
    
    return distribution, sum(latencies) / len(latencies) if latencies else float('inf')

async def run_hash_function_experiment():
    # Start peer nodes and create ClientAPI instances for each
    peer_processes = [start_peer_node(format(i, '03b')) for i in range(8)]
    client_apis = [ClientAPI(format(i, '03b')) for i in range(8)]

    # Allow time for nodes to initialize
    await asyncio.sleep(8)

    try:
        # Experiment with MD5
        md5_distribution, md5_latency = await setup_topics_with_hash_function(client_apis, hash_topic_md5)

        # Experiment with SHA-256
        sha256_distribution, sha256_latency = await setup_topics_with_hash_function(client_apis, hash_topic_sha256)

        # Print results
        print("MD5 Distribution:", md5_distribution)
        print("MD5 Average Latency:", md5_latency)
        print("SHA-256 Distribution:", sha256_distribution)
        print("SHA-256 Average Latency:", sha256_latency)

        # Plotting the results
        plot_results(md5_distribution, md5_latency, sha256_distribution, sha256_latency)
    finally:
        # Terminate peer node processes
        for process in peer_processes:
            process.terminate()
            process.wait()

def plot_results(md5_distribution, md5_latency, sha256_distribution, sha256_latency):
    nodes = list(md5_distribution.keys())
    md5_counts = list(md5_distribution.values())
    sha256_counts = list(sha256_distribution.values())

    # Plot Topic Distribution Comparison
    plt.figure(figsize=(10, 5))
    plt.plot(nodes, md5_counts, marker='o', label='MD5 Topic Distribution')
    plt.plot(nodes, sha256_counts, marker='o', label='SHA-256 Topic Distribution')
    plt.xlabel("Node ID")
    plt.ylabel("Number of Topics")
    plt.title("Topic Distribution Across Nodes (MD5 vs SHA-256)")
    plt.legend()
    plt.grid(True)
    plt.show()

    # Plot Average Latency Comparison
    plt.figure(figsize=(6, 4))
    plt.bar(['MD5', 'SHA-256'], [md5_latency, sha256_latency], color=['blue', 'green'])
    plt.xlabel("Hash Function")
    plt.ylabel("Average Latency (seconds)")
    plt.title("Average Latency for Topic Creation (MD5 vs SHA-256)")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    asyncio.run(run_hash_function_experiment())
