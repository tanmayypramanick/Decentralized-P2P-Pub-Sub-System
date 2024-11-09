import asyncio
import json
import logging
from hypercube import route_to_target
from dht_hash import hash_topic

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ClientAPI:
    def __init__(self, node_id, default_port=8000):
        self.node_id = node_id
        self.host = '127.0.0.1'
        self.default_port = default_port

    async def send_and_receive(self, target_node, message):
        routing_path = route_to_target(self.node_id, target_node)
        target_port = self.default_port + int(target_node, 2)

        try:
            reader, writer = await asyncio.open_connection(self.host, target_port)
            writer.write(json.dumps(message).encode('utf-8'))
            await writer.drain()

            data = await reader.read(1024)
            response = json.loads(data.decode('utf-8')) if data else {}
            writer.close()
            await writer.wait_closed()
            return response
        except Exception as e:
            logging.error(f"[ClientAPI] Error connecting to peer {target_node}: {e}")
            return {}

    async def create_topic(self, topic):
        target_node = hash_topic(topic)
        message = {'command': 'CREATE', 'topic': topic}
        return await self.send_and_receive(target_node, message)

    async def send_message(self, topic, message):
        target_node = hash_topic(topic)
        msg = {'command': 'PUBLISH', 'topic': topic, 'message': message}
        return await self.send_and_receive(target_node, msg)

    async def delete_topic(self, topic):
        target_node = hash_topic(topic)
        message = {'command': 'DELETE', 'topic': topic}
        return await self.send_and_receive(target_node, message)

    async def subscribe(self, topic):
        target_node = hash_topic(topic)
        message = {'command': 'SUBSCRIBE', 'topic': topic}
        response = await self.send_and_receive(target_node, message)
        # Check if the topic was found
        if response.get("status") == "Topic not found":
            logging.warning(f"[ClientAPI] Topic '{topic}' not found for subscription.")
            return {"status": "Topic not found"}
        return response

    async def pull_messages(self, topic):
        target_node = hash_topic(topic)
        message = {'command': 'PULL', 'topic': topic}
        response = await self.send_and_receive(target_node, message)
        # Return an empty list if the topic is not found
        if response.get("status") == "Topic not found":
            logging.warning(f"[ClientAPI] Topic '{topic}' not found for pulling messages.")
            return []
        return response.get('messages', [])
