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

def start_peer_node(peer_id):
    print(f"[LOG] Starting PeerNode with ID {peer_id}")
    return subprocess.Popen(
        [sys.executable, os.path.join(parent_dir, 'peer_node.py'), peer_id],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

def stop_server(server_process):
    server_process.terminate()
    try:
        server_process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        server_process.kill()

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

async def benchmark_forwarding(peer_id, target_peer_id, topic_name, retries=5, timeout=15, delay=3):
    client = ClientAPI(peer_id)
    latencies = []

    for attempt in range(retries):
        try:
            start_time = time.time()
            print(f"[LOG] Attempting to pull messages for topic '{topic_name}' from peer {target_peer_id}, attempt {attempt+1}")
            await asyncio.wait_for(client.pull_messages(topic_name), timeout=timeout)
            end_time = time.time()
            latencies.append(end_time - start_time)
            break  # Stop retrying if successful
        except asyncio.TimeoutError:
            print(f"[ERROR] Timeout accessing topic '{topic_name}' on peer {target_peer_id}, attempt {attempt+1}")
            if attempt < retries - 1:
                print(f"[LOG] Waiting {delay} seconds before retrying...")
                await asyncio.sleep(delay)

    if latencies:
        return sum(latencies) / len(latencies)
    else:
        return float('inf')  # If all attempts failed

async def setup_topic_for_peer(peer_id, topic_name):
    client = ClientAPI(peer_id)
    await client.create_topic(topic_name)
    await client.send_message(topic_name, f"Message for {topic_name}")

def run_forwarding_benchmark(num_peers, num_trials, csv_filename):
    ensure_directory_exists("data")
    with open(csv_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Number of Peers", "Average Latency (seconds)", "Max Throughput (requests/second)"])

        peer_processes = []
        for i in range(num_peers):
            peer_id = format(i, '03b')  # Binary ID
            peer_process = start_peer_node(peer_id)
            peer_processes.append(peer_process)
            time.sleep(1)

        time.sleep(5)  # Wait for all peers to initialize

        for peer_count in range(1, num_peers + 1):
            avg_latencies = []
            throughputs = []
            print(f"[LOG] Running request forwarding benchmark with {peer_count} peers for {num_trials} trials...")

            for _ in range(num_trials):
                total_latencies = []
                start_benchmark = time.time()

                # Set up a topic on each peer
                topic_name = f"topic_{uuid.uuid4()}"
                asyncio.run(setup_topic_for_peer("000", topic_name))
                time.sleep(1)

                # Forwarding requests across all peer pairs
                for i in range(peer_count):
                    for j in range(peer_count):
                        if i != j:  # Skip self-access
                            requesting_peer = format(i, '03b')
                            target_peer = format(j, '03b')
                            latency = asyncio.run(benchmark_forwarding(requesting_peer, target_peer, topic_name))
                            total_latencies.append(latency)

                end_benchmark = time.time()
                benchmark_duration = end_benchmark - start_benchmark
                avg_latency = sum(total_latencies) / len(total_latencies) if total_latencies else float('inf')
                avg_latencies.append(avg_latency)

                # Calculate throughput only if the benchmark duration is non-zero
                if benchmark_duration > 0:
                    max_throughput = len(total_latencies) / benchmark_duration
                    throughputs.append(max_throughput)
                else:
                    throughputs.append(0)

            # Calculate average results over trials
            avg_latency_across_trials = sum(avg_latencies) / len(avg_latencies) if avg_latencies else float('inf')
            avg_throughput_across_trials = sum(throughputs) / len(throughputs) if throughputs else 0

            print(f"[LOG] Results for {peer_count} peers - Avg Latency: {avg_latency_across_trials:.4f}s, Max Throughput: {avg_throughput_across_trials:.2f} req/s")
            writer.writerow([peer_count, f"{avg_latency_across_trials:.4f}", f"{avg_throughput_across_trials:.2f}"])

        for peer_process in peer_processes:
            stop_server(peer_process)

def plot_forwarding_results(csv_filename, latency_graph_filename, throughput_graph_filename):
    num_peers = []
    latencies = []
    throughputs = []

    with open(csv_filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            num_peers.append(int(row['Number of Peers']))
            latencies.append(float(row['Average Latency (seconds)']))
            throughputs.append(float(row['Max Throughput (requests/second)']))

    plt.figure()
    plt.plot(num_peers, latencies, label='Average Latency (Seconds)', color='blue', marker='o')
    plt.xlabel("Number of Peers")
    plt.ylabel("Average Latency (Seconds)")
    plt.title("Request Forwarding Latency vs Number of Peers")
    plt.grid(True)
    ensure_directory_exists("graphs")
    plt.savefig(latency_graph_filename)
    plt.show()

    plt.figure()
    plt.plot(num_peers, throughputs, label='Max Throughput (Requests/Second)', color='green', marker='o')
    plt.xlabel("Number of Peers")
    plt.ylabel("Max Throughput (Requests/Second)")
    plt.title("Request Forwarding Throughput vs Number of Peers")
    plt.grid(True)
    plt.savefig(throughput_graph_filename)
    plt.show()

if __name__ == "__main__":
    num_peers = 8  
    num_trials = 10
    csv_filename = "data/request_forwarding_benchmark.csv"
    latency_graph_filename = "graphs/request_forwarding_latency_vs_peers.png"
    throughput_graph_filename = "graphs/request_forwarding_throughput_vs_peers.png"

    run_forwarding_benchmark(num_peers, num_trials, csv_filename)
    plot_forwarding_results(csv_filename, latency_graph_filename, throughput_graph_filename)
