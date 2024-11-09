import sys
import os
import subprocess
import time
import asyncio
import statistics
import matplotlib.pyplot as plt

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from client_api import ClientAPI

async def query_indexing_server(client, topic):
    start_time = time.time()
    await client.send_and_receive({'action': 'query', 'topic': topic})
    return time.time() - start_time

async def run_peer_queries(peer_ip, peer_port, topic, num_requests):
    client = ClientAPI(peer_ip, peer_port)
    response_times = []
    for _ in range(num_requests):
        response_time = await query_indexing_server(client, topic)
        response_times.append(response_time)
    return response_times

def start_peer_node(port):
    print(f"Starting Peer Node on port {port}...")
    peer_node_path = os.path.join(parent_dir, "PeerNode.py")
    peer_node = subprocess.Popen(["python", peer_node_path, "--peer-ip", "0.0.0.0", "--peer-port", str(port)])
    return peer_node

async def measure_response_time(num_peers, num_requests):
    peers = []
    ports = list(range(8000, 8000 + num_peers))

    print(f"\nStarting {num_peers} Peer Nodes...")

    # Start Peer Nodes
    for port in ports:
        peers.append(start_peer_node(port))
        time.sleep(1)  # Allow peers to start

    # Query a single topic from the indexing server
    topic = 'News'
    tasks = []
    for port in ports:
        tasks.append(run_peer_queries("127.0.0.1", port, topic, num_requests))

    all_response_times = await asyncio.gather(*tasks)

    # Calculate the average response time
    combined_response_times = [time for peer_times in all_response_times for time in peer_times]
    avg_response_time = statistics.mean(combined_response_times)
    return avg_response_time

def plot_results(results):
    num_peers = [data[0] for data in results]
    avg_times = [data[1] for data in results]

    plt.plot(num_peers, avg_times, marker='o')
    plt.xlabel("Number of Peer Nodes")
    plt.ylabel("Average Response Time (seconds)")
    plt.title("Response Time vs Number of Peers (Fixed 1000 Requests per Peer)")
    plt.grid(True)
    plt.savefig("response_time_vs_peers.png")
    plt.show()

async def main():
    num_requests = 1000  # Set to 1000 requests per peer
    results = []

    print(f"--- Running tests with {num_requests} requests per peer ---")

    for num_peers in [2, 4, 8]:
        print(f"\n--- Testing with {num_peers} peers ---")
        avg_response_time = await measure_response_time(num_peers, num_requests)
        print(f"Average response time for {num_peers} peers: {avg_response_time:.6f} seconds")
        results.append((num_peers, avg_response_time))

    plot_results(results)

if __name__ == "__main__":
    asyncio.run(main())
