import csv
import time
import uuid
import asyncio
import os
import sys
import matplotlib.pyplot as plt
import subprocess

# Ensure the tests can find the client API and other project files
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from client_api import ClientAPI

# Start a subprocess to run a PeerNode
def start_peer_node(peer_id):
    print(f"[LOG] Starting PeerNode with ID {peer_id}")
    return subprocess.Popen(
        [sys.executable, os.path.join(parent_dir, 'peer_node.py'), peer_id],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

# Stop the server process
def stop_server(server_process):
    server_process.terminate()
    try:
        server_process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        server_process.kill()

# Ensure the directories exist for storing CSV and graph files
def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Benchmark the delete_topic API for a peer node with increased timeout and delay
async def benchmark_delete_topic(peer_id, num_topics, timeout=30, delay_between_requests=0.5):
    client = ClientAPI(peer_id)  # Pass peer_id to ClientAPI
    latencies = []
    start_time = time.time()

    # Pre-create topics for deletion
    topics = [f"topic_{uuid.uuid4()}" for _ in range(num_topics)]
    for topic in topics:
        await client.create_topic(topic)  # Ensure each topic is created first

    # Delete each topic and measure latency
    for topic_name in topics:
        topic_start_time = time.time()
        try:
            print(f"[LOG] Deleting topic: {topic_name} on peer ID: {peer_id}")
            await asyncio.wait_for(client.delete_topic(topic_name), timeout=timeout)
            topic_end_time = time.time()
            latencies.append(topic_end_time - topic_start_time)
        except asyncio.TimeoutError:
            print(f"[ERROR] Timeout: Deleting topic {topic_name} on peer ID {peer_id}")
        
        # Adding a small delay between requests to reduce contention
        await asyncio.sleep(delay_between_requests)

    end_time = time.time()
    throughput = num_topics / (end_time - start_time)
    avg_latency = sum(latencies) / len(latencies) if latencies else float('inf')

    print(f"[LOG] Completed {num_topics} topic deletions on peer ID: {peer_id}")
    return throughput, avg_latency

# Function to run the benchmark and save results to CSV
def run_delete_topic_benchmark(num_peers, num_topics, csv_filename):
    # Prepare results CSV
    ensure_directory_exists("data")  # Ensure the data directory exists
    with open(csv_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Number of Peers", "Number of Topics", "Throughput (topics/second)", "Average Latency (seconds)"])

        # Start the required number of peer nodes and give them time to start up
        peer_processes = []
        for i in range(num_peers):
            peer_id = format(i, '03b')  # Binary ID (e.g., "000", "001", etc.)
            peer_process = start_peer_node(peer_id)
            peer_processes.append(peer_process)
            time.sleep(5)  # Increased delay to ensure each peer starts properly

        # Delay to ensure all peers are fully initialized before benchmarking
        time.sleep(5)

        # Run benchmark for each peer count
        for peer_count in range(1, num_peers + 1):
            total_throughput = 0
            total_latency = 0

            print(f"[LOG] Running benchmark with {peer_count} peers...")

            # Run benchmark for each peer
            for i in range(peer_count):
                peer_id = format(i, '03b')

                # Run benchmark asynchronously with extended timeout and delay
                throughput, avg_latency = asyncio.run(benchmark_delete_topic(peer_id, num_topics))

                total_throughput += throughput
                total_latency += avg_latency

            avg_throughput = total_throughput / peer_count
            avg_latency = total_latency / peer_count
            print(f"[LOG] Benchmark result for {peer_count} peers: {num_topics} topics, Throughput: {avg_throughput:.2f} topics/sec, Avg Latency: {avg_latency:.6f} sec")
            writer.writerow([peer_count, num_topics, avg_throughput, avg_latency])

        # Stop all peers after the benchmark
        for peer_process in peer_processes:
            stop_server(peer_process)

# Plot the results from the CSV file
def plot_delete_topic_graph(csv_filename, throughput_graph_filename, latency_graph_filename):
    num_peers = []
    throughputs = []
    latencies = []

    with open(csv_filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            num_peers.append(int(row['Number of Peers']))
            throughputs.append(float(row['Throughput (topics/second)']))
            latencies.append(float(row['Average Latency (seconds)']))

    # Plot Throughput Graph
    plt.figure()
    plt.plot(num_peers, throughputs, label='Throughput (Topics/Second)', color='blue', marker='o')
    plt.xlabel("Number of Peers")
    plt.ylabel("Throughput (Topics/Second)")
    plt.title("Delete Topic Throughput vs Number of Peers")
    plt.grid(True)
    ensure_directory_exists("graphs")
    plt.savefig(throughput_graph_filename)
    plt.show()

    # Plot Latency Graph
    plt.figure()
    plt.plot(num_peers, latencies, label='Latency (Seconds)', color='red', marker='o')
    plt.xlabel("Number of Peers")
    plt.ylabel("Average Latency (Seconds)")
    plt.title("Delete Topic Latency vs Number of Peers")
    plt.grid(True)
    plt.savefig(latency_graph_filename)
    plt.show()

if __name__ == "__main__":
    num_peers = 8  
    num_topics = 3
    csv_filename = "data/delete_topic_benchmark.csv"
    throughput_graph_filename = "graphs/delete_topic_throughput_vs_peers.png"
    latency_graph_filename = "graphs/delete_topic_latency_vs_peers.png"

    # Run the benchmark and plot the results
    run_delete_topic_benchmark(num_peers, num_topics, csv_filename)
    plot_delete_topic_graph(csv_filename, throughput_graph_filename, latency_graph_filename)
