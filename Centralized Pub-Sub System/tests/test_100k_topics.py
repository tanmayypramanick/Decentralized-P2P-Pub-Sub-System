import sys
import os
import asyncio
import time
import statistics
import matplotlib.pyplot as plt
import subprocess
import psutil

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

from client_api import ClientAPI

def start_indexing_server():
    """Start the Indexing Server programmatically."""
    print("Starting Indexing Server...")
    server_process = subprocess.Popen(
        [sys.executable, os.path.join(parent_dir, 'IndexingServer.py')],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(2)  # Wait a few seconds for the server to initialize
    return server_process

def stop_indexing_server(server_process):
    """Stop the Indexing Server process."""
    print("Stopping Indexing Server...")
    if server_process and psutil.pid_exists(server_process.pid):
        server_process.terminate()
        try:
            server_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            server_process.kill()

async def register_topics(client, num_topics):
    """Register topics with the indexing server concurrently."""
    batch_size = 1000  
    tasks = []
    for i in range(num_topics):
        topic = f"topic_{i}"
        tasks.append(client.send_and_receive({
            'action': 'topic_update',
            'topics': [topic],
            'peer_ip': '127.0.0.1',
            'peer_port': 8000
        }))
        if len(tasks) >= batch_size:
            await asyncio.gather(*tasks)
            tasks = []
    # Register any remaining topics
    if tasks:
        await asyncio.gather(*tasks)

async def query_topic(client, topic):
    """Query a single topic from the indexing server and measure the response time."""
    start_time = time.time()
    await client.send_and_receive({'action': 'query', 'topic': topic})
    return time.time() - start_time

async def run_query_tests(client, num_queries):
    """Run query tests for the given number of queries."""
    response_times = []
    for i in range(num_queries):
        topic = f"topic_{i % 100000}"  
        response_time = await query_topic(client, topic)
        response_times.append(response_time)
    return response_times

def plot_results(results):
    """Plot the results of the query response times."""
    num_queries = [data[0] for data in results]
    avg_times = [data[1] for data in results]

    plt.plot(num_queries, avg_times, marker='o')
    plt.xlabel("Number of Queries")
    plt.ylabel("Average Response Time (seconds)")
    plt.title("Query Response Time with Registered Topics")
    plt.grid(True)
    plt.savefig("query_response_time_with_registered_topics.png")
    plt.show()

async def main():
    # Start Indexing Server
    server_process = start_indexing_server()

    # Client API for the peer to communicate with the indexing server
    client = ClientAPI("127.0.0.1", 9090)

    # Wait a few seconds to ensure the indexing server is ready
    print("Waiting for Indexing Server to be ready...")
    await asyncio.sleep(2)

    num_topics = 100000  # Adjusted from 1 million to 100,000
    print(f"Registering {num_topics} topics to the Indexing Server...")
    start_time = time.time()
    await register_topics(client, num_topics)
    print(f"Finished registering {num_topics} topics in {time.time() - start_time:.2f} seconds!")

    # Step 2: Measure response time for querying topics
    print("Measuring response time for querying topics...")
    num_queries_list = [100, 1000, 5000, 10000]  
    results = []

    for num_queries in num_queries_list:
        print(f"Running query test with {num_queries} queries...")
        response_times = await run_query_tests(client, num_queries)
        avg_response_time = statistics.mean(response_times)
        print(f"Average response time for {num_queries} queries: {avg_response_time:.6f} seconds")
        results.append((num_queries, avg_response_time))

    # Step 3: Plot the results
    plot_results(results)

    # Stop the Indexing Server
    stop_indexing_server(server_process)

if __name__ == "__main__":
    asyncio.run(main())
