import asyncio
import time
import os
import sys
import random
import matplotlib.pyplot as plt
import uuid

# Ensure the tests can find the client API and other project files
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from client_api import ClientAPI

async def measure_latency(client, topic, latency_ms):
    """Measure the latency of a topic lookup with added artificial network delay."""
    await asyncio.sleep(latency_ms / 1000.0)  # Simulate network latency
    start_time = time.time()
    await client.pull_messages(topic)  # Simulate a DHT operation
    end_time = time.time()
    return end_time - start_time

async def run_latency_experiment(latency_levels, num_lookups=50):
    # Assume client API is running on one peer node for simplicity
    client = ClientAPI(node_id="000")
    topic = f"topic_{uuid.uuid4()}"  # Use a single topic for repeated lookups

    latencies = []
    for latency_ms in latency_levels:
        print(f"[LOG] Running with simulated network latency of {latency_ms}ms")
        latency_sum = 0

        for _ in range(num_lookups):
            lookup_time = await measure_latency(client, topic, latency_ms)
            latency_sum += lookup_time

        avg_latency = latency_sum / num_lookups
        latencies.append(avg_latency)
        print(f"Average latency for {latency_ms}ms network delay: {avg_latency:.4f}s")

    plot_latency_results(latency_levels, latencies)

def plot_latency_results(latency_levels, latencies):
    plt.figure(figsize=(10, 6))
    plt.plot(latency_levels, latencies, marker='o', color='blue')
    plt.xlabel("Simulated Network Latency (ms)")
    plt.ylabel("Average DHT Lookup Time (seconds)")
    plt.title("Impact of Network Latency on DHT Lookup Times")
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    latency_levels = [0, 10, 50, 100, 200]  # Various simulated network delays
    asyncio.run(run_latency_experiment(latency_levels))
