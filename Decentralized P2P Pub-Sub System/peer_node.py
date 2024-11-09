import asyncio
import json
import logging
import sys
from dht_hash import hash_topic
from hypercube import get_neighbors

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PeerNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.port = 8000 + int(node_id, 2)
        self.topics = {}
        self.neighbors = get_neighbors(node_id)

    async def handle_request(self, reader, writer):
        data = await reader.read(1024)
        message = json.loads(data.decode())
        action = message.get("command")
        topic = message.get("topic")
        target_node = hash_topic(topic)  # Target node based on topic hash

        # Check if the request should be handled locally or forwarded
        if target_node == self.node_id:
            response = self.process_local_request(action, topic, message)
        else:
            response = await self.forward_request(target_node, message)

        writer.write(json.dumps(response).encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()

    def process_local_request(self, action, topic, message):
        """Handle requests that target this node directly."""
        if action == "CREATE":
            return self.create_topic(topic)
        elif action == "PUBLISH":
            return self.publish_message(topic, message.get("message"))
        elif action == "DELETE":
            return self.delete_topic(topic)
        elif action == "SUBSCRIBE":
            return self.subscribe_to_topic(topic)
        elif action == "PULL":
            return {"messages": self.pull_topic_messages(topic)}
        else:
            return {"status": "Unknown action"}

    async def forward_request(self, target_node, message):
        """Forward request to the appropriate neighbor node."""
        path = get_neighbors(self.node_id)  # Use routing to get next neighbor
        adaptive_timeout = 5 + (len(path) * 2)  # Adjust timeout based on hop count
        
        for neighbor in path:
            try:
                logging.info(f"[{self.node_id}] Forwarding request to {neighbor} with timeout {adaptive_timeout} seconds")
                response = await asyncio.wait_for(self.send_request(neighbor, message), timeout=adaptive_timeout)
                return response
            except asyncio.TimeoutError:
                logging.error(f"[{self.node_id}] Timeout while forwarding to {neighbor}")
            except Exception as e:
                logging.error(f"[{self.node_id}] Error while forwarding to {neighbor}: {e}")
        
        return {"status": "Failed to forward request"}

    async def send_request(self, target_node, message):
        """Send a JSON request to another peer node."""
        reader, writer = await asyncio.open_connection("localhost", 8000 + int(target_node, 2))
        writer.write(json.dumps(message).encode())
        await writer.drain()
        
        data = await reader.read(1024)
        response = json.loads(data.decode())
        
        writer.close()
        await writer.wait_closed()
        return response

    # Existing methods for topic operations
    def create_topic(self, topic):
        if topic not in self.topics:
            self.topics[topic] = []
            logging.info(f"[{self.node_id}] Created topic '{topic}'")
            return {"status": "Topic created"}
        else:
            logging.info(f"[{self.node_id}] Topic '{topic}' already exists")
            return {"status": "Topic already exists"}

    def publish_message(self, topic, message):
        if topic in self.topics:
            self.topics[topic].append(message)
            logging.info(f"[{self.node_id}] Message published to topic '{topic}'")
            return {"status": "Message published"}
        else:
            logging.warning(f"[{self.node_id}] Topic '{topic}' not found")
            return {"status": "Topic not found"}

    def delete_topic(self, topic):
        if topic in self.topics:
            del self.topics[topic]
            logging.info(f"[{self.node_id}] Deleted topic '{topic}'")
            return {"status": "Topic deleted"}
        else:
            logging.warning(f"[{self.node_id}] Topic '{topic}' not found")
            return {"status": "Topic not found"}

    def subscribe_to_topic(self, topic):
        if topic in self.topics:
            logging.info(f"[{self.node_id}] Subscription to topic '{topic}' successful")
            return {"status": "Subscribed"}
        else:
            logging.warning(f"[{self.node_id}] Topic '{topic}' not found for subscription")
            return {"status": "Topic not found"}

    def pull_topic_messages(self, topic):
        if topic in self.topics:
            messages = self.topics[topic]
            logging.info(f"[{self.node_id}] Pulled messages from topic '{topic}'")
            return messages
        else:
            logging.warning(f"[{self.node_id}] Topic '{topic}' not found")
            return []
    
    async def start_server(self):
        server = await asyncio.start_server(self.handle_request, "localhost", self.port)
        logging.info(f"[{self.node_id}] Server started on port {self.port}")
        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python peer_node.py <node_id>")
        sys.exit(1)

    node_id = sys.argv[1]
    node = PeerNode(node_id)
    asyncio.run(node.start_server())
