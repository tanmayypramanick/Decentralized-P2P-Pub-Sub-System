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

async def benchmark_subscribe(peer_id, num_topics, timeout=20, delay_between_requests=2, retries=3):
    client = ClientAPI(peer_id)
    latencies = []
    start_time = time.time()

    for _ in range(num_topics):
        topic_name = f"topic_{uuid.uuid4()}"

        # Ensure the topic exists before subscribing
        await client.create_topic(topic_name)

        # Measure latency for each subscription
        subscribe_start_time = time.time()
        for attempt in range(retries):
            try:
                print(f"[LOG] Subscribing to topic: {topic_name} on peer ID: {peer_id}, attempt {attempt+1}")
                await asyncio.wait_for(client.subscribe(topic_name), timeout=timeout)
                subscribe_end_time = time.time()
                latencies.append(subscribe_end_time - subscribe_start_time)
                break
            except asyncio.TimeoutError:
                print(f"[ERROR] Timeout: Subscribing to topic {topic_name} on peer ID {peer_id}, attempt {attempt+1}")
                if attempt == retries - 1:
                    print(f"[ERROR] Failed to subscribe to {topic_name} on peer ID {peer_id} after {retries} attempts")
        
        # Adding a longer delay between requests
        await asyncio.sleep(delay_between_requests)

    end_time = time.time()
    throughput = num_topics / (end_time - start_time)
    avg_latency = sum(latencies) / len(latencies) if latencies else float('inf')

    print(f"[LOG] Completed {num_topics} subscriptions on peer ID: {peer_id}")
    return throughput, avg_latency

def run_subscribe_benchmark(num_peers, num_topics, csv_filename):
    ensure_directory_exists("data")
    with open(csv_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Number of Peers", "Number of Topics", "Throughput (subscriptions/second)", "Average Latency (seconds)"])

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

            print(f"[LOG] Running benchmark with {peer_count} peers...")

            for i in range(peer_count):
                peer_id = format(i, '03b')
                throughput, avg_latency = asyncio.run(benchmark_subscribe(peer_id, num_topics))

                total_throughput += throughput
                total_latency += avg_latency

            avg_throughput = total_throughput / peer_count
            avg_latency = total_latency / peer_count
            print(f"[LOG] Benchmark result for {peer_count} peers: {num_topics} topics, Throughput: {avg_throughput:.2f} subscriptions/sec, Avg Latency: {avg_latency:.6f} sec")
            writer.writerow([peer_count, num_topics, avg_throughput, avg_latency])

        for peer_process in peer_processes:
            stop_server(peer_process)

def plot_subscribe_graph(csv_filename, throughput_graph_filename, latency_graph_filename):
    num_peers = []
    throughputs = []
    latencies = []

    with open(csv_filename, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            num_peers.append(int(row['Number of Peers']))
            throughputs.append(float(row['Throughput (subscriptions/second)']))
            latencies.append(float(row['Average Latency (seconds)']))

    plt.figure()
    plt.plot(num_peers, throughputs, label='Throughput (Subscriptions/Second)', color='blue', marker='o')
    plt.xlabel("Number of Peers")
    plt.ylabel("Throughput (Subscriptions/Second)")
    plt.title("Subscribe API Throughput vs Number of Peers")
    plt.grid(True)
    ensure_directory_exists("graphs")
    plt.savefig(throughput_graph_filename)
    plt.show()

    plt.figure()
    plt.plot(num_peers, latencies, label='Latency (Seconds)', color='red', marker='o')
    plt.xlabel("Number of Peers")
    plt.ylabel("Average Latency (Seconds)")
    plt.title("Subscribe API Latency vs Number of Peers")
    plt.grid(True)
    plt.savefig(latency_graph_filename)
    plt.show()

if __name__ == "__main__":
    num_peers = 8  
    num_topics = 3  
    csv_filename = "data/subscribe_benchmark.csv"
    throughput_graph_filename = "graphs/subscribe_throughput_vs_peers.png"
    latency_graph_filename = "graphs/subscribe_latency_vs_peers.png"

    run_subscribe_benchmark(num_peers, num_topics, csv_filename)
    plot_subscribe_graph(csv_filename, throughput_graph_filename, latency_graph_filename)
