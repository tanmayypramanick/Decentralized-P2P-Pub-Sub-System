import sys
import os
import subprocess
import time
import asyncio

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)
from client_api import ClientAPI

def start_indexing_server():
    print("Starting Indexing Server...")
    indexing_server_path = os.path.join(parent_dir, "IndexingServer.py")
    indexing_server = subprocess.Popen(["python", indexing_server_path])
    return indexing_server

def start_peer_node(port):
    print(f"Starting Peer Node on port {port}...")
    peer_node_path = os.path.join(parent_dir, "PeerNode.py")
    peer_node = subprocess.Popen(["python", peer_node_path, "--peer-ip", "0.0.0.0", "--peer-port", str(port)])
    return peer_node

async def publish_and_subscribe(peer_ip, peer_port, topic, message):
    client = ClientAPI(peer_ip, peer_port)
    
    # Create the topic on the peer
    print(f"\n--- Creating topic '{topic}' on Peer {peer_ip}:{peer_port} ---")
    await client.create_topic(topic)
    
    # Publish a message to the topic
    print(f"Publishing message '{message}' to topic '{topic}' on Peer {peer_ip}:{peer_port}")
    await client.send_message(topic, message)

    # Subscribe and pull messages from the topic
    print(f"Subscribing and pulling messages from topic '{topic}' on Peer {peer_ip}:{peer_port}")
    await client.subscribe(topic)
    messages = await client.pull_messages(topic)

    print(f"Pulled messages from topic '{topic}': {messages}")

    return messages

async def test_delete_topic(peer_ip, peer_port, topic):
    client = ClientAPI(peer_ip, peer_port)
    
    # Delete the topic from the peer
    print(f"\n--- Deleting topic '{topic}' on Peer {peer_ip}:{peer_port} ---")
    await client.delete_topic(topic)
    print(f"Topic '{topic}' deleted successfully.")
    
    # Attempt to pull messages from the deleted topic (should fail)
    print(f"Attempting to pull messages from deleted topic '{topic}' (expected to fail)...")
    messages = await client.pull_messages(topic)
    
    if messages:
        print(f"Error: Pulled messages from deleted topic '{topic}': {messages}")
    else:
        print(f"Confirmed: No messages found for deleted topic '{topic}'.")

async def test_apis():
    peer_info = [
        ("127.0.0.1", 8081, "News", "Breaking news on peer 8081"),
        ("127.0.0.1", 8082, "Sports", "Sports update from peer 8082"),
        ("127.0.0.1", 8083, "Movies", "New movie release from peer 8083"),
    ]
    
    tasks = []
    
    # Test publishing and subscribing for each peer node
    for peer_ip, peer_port, topic, message in peer_info:
        tasks.append(publish_and_subscribe(peer_ip, peer_port, topic, message))
    
    # Run all tasks concurrently
    await asyncio.gather(*tasks)

    # Test deleting topics for each peer node
    for peer_ip, peer_port, topic, _ in peer_info:
        await test_delete_topic(peer_ip, peer_port, topic)

if __name__ == "__main__":
    indexing_server = start_indexing_server()
    time.sleep(2)  # Wait for indexing server to start
    
    peers = []
    for port in [8081, 8082, 8083]:
        peers.append(start_peer_node(port))
        time.sleep(1)  # Small delay to allow peers to start sequentially

    print("\nIndexing Server and Peers are running...")

    # Wait a bit for everything to be ready
    time.sleep(5)

    # Start testing the APIs (publishing/subscribing/deleting)
    try:
        asyncio.run(test_apis())
    except Exception as e:
        print(f"Error occurred during API test: {str(e)}")

    # Keep running until interrupted
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\nShutting down...")
        indexing_server.terminate()
        for peer in peers:
            peer.terminate()
