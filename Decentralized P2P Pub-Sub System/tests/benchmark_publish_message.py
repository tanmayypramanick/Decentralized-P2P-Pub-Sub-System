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

# Benchmark the publish_message API for a peer node with an increased timeout and delay
async def benchmark_publish_message(peer_id, topic_name, num_messages, timeout=20, delay_between_requests=0.3):
    client = ClientAPI(peer_id)  # Pass peer_id to ClientAPI
    latencies = []
    start_time = time.time()

    # Pre-create the topic for publishing messages
    await client.create_topic(topic_name)  

    # Publish each message and measure latency
    for _ in range(num_messages):
        message_content = f"message_{uuid.uuid4()}"
        message_start_time = time.time()
        try:
            print(f"[LOG] Publishing message: {message_content} to topic: {topic_name} on peer ID: {peer_id}")
            await asyncio.wait_for(client.send_message(topic_name, message_content), timeout=timeout)
            message_end_time = time.time()
            latencies.append(message_end_time - message_start_time)
        except asyncio.TimeoutError:
            print(f"[ERROR] Timeout: Publishing message to topic {topic_name} on peer ID {peer_id}")
        
        # Adding a small delay between requests to reduce contention
        await asyncio.sleep(delay_between_requests)

    end_time = time.time()
    throughput = num_messages / (end_time - start_time)
    avg_latency = sum(latencies) / len(latencies) if latencies else float('inf')

    print(f"[LOG] Completed publishing {num_messages} messages on peer ID: {peer_id}")
    return throughput, avg_latency

# Function to run the benchmark and save results to CSV
def run_publish_message_benchmark(num_peers, num_messages, csv_filename):
    # Prepare results CSV
    ensure_directory_exists("data")  # Ensure the data directory exists
    with open(csv_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Number of Peers", "Number of Messages", "Throughput (messages/second)", "Average Latency (seconds)"])

        # Start the required number of peer nodes and give them time to start up
        peer_processes = []
        for i in range(num_peers):
            peer_id = format(i, '03b')  # Binary ID (e.g., "000", "001", etc.)
            peer_process = start_peer_node(peer_id)
            peer_processes.append(peer_process)
            time.sleep(5)  # Delay to ensure each peer starts properly

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
                topic_name = f"topic_{uuid.uuid4()}"  # Unique topic for each benchmark run

                # Run benchmark asynchronously with extended timeout and delay
                throughput, avg_latency = asyncio.run(benchmark_publish_message(peer_id, topic_name, num_messages))

                total_throughput += throughput
                total_latency += avg_latency

            avg_throughput = total_throughput / peer_count
            avg_latency = total_latency / peer_count
            print(f"[LOG] Benchmark result for {peer_count} peers: {num_messages} messages, Throughput: {avg_throughput:.2f} messages/sec, Avg Latency: {avg_latency:.6f} sec")
            writer.writerow([peer_count, num_messages, avg_throughput, avg_latency])

        # Stop all peers after the benchmark
        for peer_process in peer_processes:
            stop_server(peer_process)

# Plot the results from the CSV file
def plot_publish_message_graph(csv_filename, throughput_graph_filename, latency_graph_filename):
    num_peers = []
    throughputs = []
    latencies = []

    with open(csv_filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            num_peers.append(int(row['Number of Peers']))
            throughputs.append(float(row['Throughput (messages/second)']))
            latencies.append(float(row['Average Latency (seconds)']))

    # Plot Throughput Graph
    plt.figure()
    plt.plot(num_peers, throughputs, label='Throughput (Messages/Second)', color='blue', marker='o')
    plt.xlabel("Number of Peers")
    plt.ylabel("Throughput (Messages/Second)")
    plt.title("Publish Message Throughput vs Number of Peers")
    plt.grid(True)
    ensure_directory_exists("graphs")
    plt.savefig(throughput_graph_filename)
    plt.show()

    # Plot Latency Graph
    plt.figure()
    plt.plot(num_peers, latencies, label='Latency (Seconds)', color='red', marker='o')
    plt.xlabel("Number of Peers")
    plt.ylabel("Average Latency (Seconds)")
    plt.title("Publish Message Latency vs Number of Peers")
    plt.grid(True)
    plt.savefig(latency_graph_filename)
    plt.show()

if __name__ == "__main__":
    num_peers = 8  
    num_messages = 5
    csv_filename = "data/publish_message_benchmark.csv"
    throughput_graph_filename = "graphs/publish_message_throughput_vs_peers.png"
    latency_graph_filename = "graphs/publish_message_latency_vs_peers.png"

    # Run the benchmark and plot the results
    run_publish_message_benchmark(num_peers, num_messages, csv_filename)
    plot_publish_message_graph(csv_filename, throughput_graph_filename, latency_graph_filename)
