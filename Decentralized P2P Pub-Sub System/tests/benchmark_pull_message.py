import csv
import time
import uuid
import asyncio
import os
import sys
import matplotlib.pyplot as plt
import subprocess

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

# Benchmark the pull_message API for a peer node with delay and retries
async def benchmark_pull_messages(peer_id, topic_name, num_pulls, timeout=20, delay_between_pulls=2, retries=3):
    client = ClientAPI(peer_id)
    latencies = []
    start_time = time.time()

    for _ in range(num_pulls):
        pull_start_time = time.time()
        for attempt in range(retries):
            try:
                print(f"[LOG] Pulling messages from topic: {topic_name} on peer ID: {peer_id}, attempt {attempt+1}")
                messages = await asyncio.wait_for(client.pull_messages(topic_name), timeout=timeout)
                pull_end_time = time.time()
                latencies.append(pull_end_time - pull_start_time)
                print(f"[LOG] Pulled {len(messages)} messages from topic '{topic_name}'")
                break
            except asyncio.TimeoutError:
                print(f"[ERROR] Timeout: Pulling messages from topic {topic_name} on peer ID {peer_id}, attempt {attempt+1}")
                if attempt == retries - 1:
                    print(f"[ERROR] Failed to pull messages from {topic_name} on peer ID {peer_id} after {retries} attempts")

        await asyncio.sleep(delay_between_pulls)

    end_time = time.time()
    throughput = num_pulls / (end_time - start_time)
    avg_latency = sum(latencies) / len(latencies) if latencies else float('inf')

    print(f"[LOG] Completed {num_pulls} message pulls on peer ID: {peer_id}")
    return throughput, avg_latency

# Function to run the benchmark and save results to CSV
def run_pull_messages_benchmark(num_peers, num_pulls, num_publish_messages, csv_filename):
    ensure_directory_exists("data")
    with open(csv_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Number of Peers", "Number of Pulls", "Throughput (pulls/second)", "Average Latency (seconds)"])

        peer_processes = []
        for i in range(num_peers):
            peer_id = format(i, '03b')
            peer_process = start_peer_node(peer_id)
            peer_processes.append(peer_process)
            time.sleep(3)

        time.sleep(5)

        for peer_count in range(1, num_peers + 1):
            total_throughput = 0
            total_latency = 0

            print(f"[LOG] Running pull messages benchmark with {peer_count} peers...")

            for i in range(peer_count):
                peer_id = format(i, '03b')
                topic_name = f"topic_{uuid.uuid4()}"  # Unique topic for each benchmark run
                message_content = f"test_message_{uuid.uuid4()}"
                
                # Pre-create the topic and publish messages before pulling
                client = ClientAPI(peer_id)
                asyncio.run(client.create_topic(topic_name))
                for _ in range(num_publish_messages):
                    asyncio.run(client.send_message(topic_name, message_content))

                # Run pull_messages benchmark asynchronously with extended timeout and delay
                throughput, avg_latency = asyncio.run(benchmark_pull_messages(peer_id, topic_name, num_pulls))

                total_throughput += throughput
                total_latency += avg_latency

            avg_throughput = total_throughput / peer_count
            avg_latency = total_latency / peer_count
            print(f"[LOG] Benchmark result for {peer_count} peers: {num_pulls} pulls, Throughput: {avg_throughput:.2f} pulls/sec, Avg Latency: {avg_latency:.6f} sec")
            writer.writerow([peer_count, num_pulls, avg_throughput, avg_latency])

        for peer_process in peer_processes:
            stop_server(peer_process)

def plot_pull_messages_graph(csv_filename, throughput_graph_filename, latency_graph_filename):
    num_peers = []
    throughputs = []
    latencies = []

    with open(csv_filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            num_peers.append(int(row['Number of Peers']))
            throughputs.append(float(row['Throughput (pulls/second)']))
            latencies.append(float(row['Average Latency (seconds)']))

    plt.figure()
    plt.plot(num_peers, throughputs, label='Throughput (Pulls/Second)', color='blue', marker='o')
    plt.xlabel("Number of Peers")
    plt.ylabel("Throughput (Pulls/Second)")
    plt.title("Pull Messages Throughput vs Number of Peers")
    plt.grid(True)
    ensure_directory_exists("graphs")
    plt.savefig(throughput_graph_filename)
    plt.show()

    plt.figure()
    plt.plot(num_peers, latencies, label='Latency (Seconds)', color='red', marker='o')
    plt.xlabel("Number of Peers")
    plt.ylabel("Average Latency (Seconds)")
    plt.title("Pull Messages Latency vs Number of Peers")
    plt.grid(True)
    plt.savefig(latency_graph_filename)
    plt.show()

if __name__ == "__main__":
    num_peers = 8  
    num_pulls = 3  
    num_publish_messages = 1
    csv_filename = "data/pull_message_benchmark.csv"
    throughput_graph_filename = "graphs/pull_message_throughput_vs_peers.png"
    latency_graph_filename = "graphs/pull_message_latency_vs_peers.png"

    run_pull_messages_benchmark(num_peers, num_pulls, num_publish_messages, csv_filename)
    plot_pull_messages_graph(csv_filename, throughput_graph_filename, latency_graph_filename)
