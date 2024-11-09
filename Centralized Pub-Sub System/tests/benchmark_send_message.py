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
def start_peer_node(peer_port):
    print(f"[LOG] Starting PeerNode on port {peer_port}")
    return subprocess.Popen([sys.executable, os.path.join(parent_dir, 'PeerNode.py'), "--peer-ip", "0.0.0.0", "--peer-port", str(peer_port)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

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

# Benchmark the send_message API for a peer node
async def benchmark_send_message(peer_ip, peer_port, topic_name, num_messages):
    client = ClientAPI(peer_ip, peer_port)
    latencies = []
    start_time = time.time()

    # Send multiple messages to the topic
    for _ in range(num_messages):
        message = f"message_{uuid.uuid4()}"

        # Measure latency for each message sent
        message_start_time = time.time()
        print(f"[LOG] Sending message: {message} to topic: {topic_name} on {peer_ip}:{peer_port}")
        await client.send_message(topic_name, message)
        message_end_time = time.time()

        latencies.append(message_end_time - message_start_time)

    end_time = time.time()
    throughput = num_messages / (end_time - start_time)
    avg_latency = sum(latencies) / len(latencies)  # Average latency

    print(f"[LOG] Completed sending {num_messages} messages to {topic_name} on {peer_ip}:{peer_port}")
    return throughput, avg_latency

# Create a topic on the peer before sending messages
async def create_topic_for_peer(peer_ip, peer_port, topic_name):
    client = ClientAPI(peer_ip, peer_port)
    print(f"[LOG] Creating topic: {topic_name} on {peer_ip}:{peer_port}")
    await client.create_topic(topic_name)

# Main function to run the benchmark and save results to CSV
async def run_send_message_benchmark(num_peers, num_messages, csv_filename):
    # Wait for the user to start the IndexingServer manually
    print("[LOG] Please ensure the Indexing Server is started manually.")
    input("[LOG] Press Enter once IndexingServer is running...")

    # Prepare results CSV
    ensure_directory_exists("data")  # Ensure the data directory exists
    with open(csv_filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Number of Peers", "Number of Messages", "Throughput (messages/second)", "Average Latency (seconds)"])

        # Run benchmark for 1 to num_peers
        for peer_count in range(1, num_peers + 1):
            peer_processes = []
            print(f"[LOG] Running benchmark with {peer_count} peers...")

            # Start the required number of peer nodes
            for i in range(peer_count):
                peer_port = 8000 + i
                peer_process = start_peer_node(peer_port)
                peer_processes.append(peer_process)
                time.sleep(1)

            total_throughput = 0
            total_latency = 0

            # Run benchmark for each peer
            for peer_id in range(peer_count):
                peer_ip = "127.0.0.1"
                peer_port = 8000 + peer_id
                topic_name = f"topic_{uuid.uuid4()}"  # Creating a unique topic for each peer

                # Pre-create a topic before sending messages
                await create_topic_for_peer(peer_ip, peer_port, topic_name)

                # Run benchmark synchronously (without threading for now)
                throughput, avg_latency = await benchmark_send_message(peer_ip, peer_port, topic_name, num_messages)

                total_throughput += throughput
                total_latency += avg_latency

            avg_throughput = total_throughput / peer_count
            avg_latency = total_latency / peer_count
            print(f"[LOG] Benchmark result for {peer_count} peers: {num_messages} messages, Throughput: {avg_throughput:.2f} messages/sec, Avg Latency: {avg_latency:.6f} sec")
            writer.writerow([peer_count, num_messages, avg_throughput, avg_latency])

            # Stop the peers after the benchmark
            for peer_process in peer_processes:
                stop_server(peer_process)

# Plot the results from the CSV file
def plot_send_message_graph(csv_filename, throughput_graph_filename, latency_graph_filename):
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
    plt.title("Send Message Throughput vs Number of Peers")
    plt.grid(True)
    ensure_directory_exists("graphs")
    plt.savefig(throughput_graph_filename)
    plt.show()

    # Plot Latency Graph
    plt.figure()
    plt.plot(num_peers, latencies, label='Latency (Seconds)', color='red', marker='o')
    plt.xlabel("Number of Peers")
    plt.ylabel("Average Latency (Seconds)")
    plt.title("Send Message Latency vs Number of Peers")
    plt.grid(True)
    plt.savefig(latency_graph_filename)
    plt.show()

if __name__ == "__main__":
    num_peers = 8  
    num_messages = 100  
    csv_filename = "data/send_message_benchmark.csv"
    throughput_graph_filename = "graphs/send_message_throughput_vs_peers.png"
    latency_graph_filename = "graphs/send_message_latency_vs_peers.png"

    # Run the benchmark and plot the results
    asyncio.run(run_send_message_benchmark(num_peers, num_messages, csv_filename))
    plot_send_message_graph(csv_filename, throughput_graph_filename, latency_graph_filename)
