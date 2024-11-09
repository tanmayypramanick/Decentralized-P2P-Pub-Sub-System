import asyncio
import json
import time

class IndexingServer:
    def __init__(self, host='127.0.0.1', port=9090):
        self.host = host
        self.port = port
        self.topics = {}  # Storing topics and the peers that host them

    async def handle_client(self, reader, writer):
        try:
            data = await reader.read(1024)
            message = data.decode().strip()
            
            try:
                message = json.loads(message)
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                writer.write(json.dumps({'error': 'Invalid message format'}).encode())
                await writer.drain()
                writer.close()
                return

            action = message.get('action')
            peer_ip = message.get('peer_ip')
            peer_port = message.get('peer_port')

            if action == 'register':
                self.log_event(f"Peer registered from {peer_ip}, {peer_port}")
            elif action == 'topic_update':
                topics = message.get('topics', [])
                for topic in topics:
                    if topic not in self.topics:
                        self.topics[topic] = []
                    if (peer_ip, peer_port) not in self.topics[topic]:
                        self.topics[topic].append((peer_ip, peer_port))
                self.log_event(f"Publisher hosted topics {topics} from {peer_ip}, {peer_port}")
            elif action == 'topic_delete':
                topics = message.get('topics', [])
                for topic in topics:
                    if topic in self.topics:
                        self.topics[topic] = [
                            peer for peer in self.topics[topic] if peer != (peer_ip, peer_port)
                        ]
                        if not self.topics[topic]:
                            del self.topics[topic]
                self.log_event(f"Publisher deleted topics {topics} from {peer_ip}, {peer_port}")
            elif action == 'unregister':
                topics = message.get('topics', [])
                for topic in topics:
                    if topic in self.topics:
                        self.topics[topic] = [
                            peer for peer in self.topics[topic] if peer != (peer_ip, peer_port)
                        ]
                        if not self.topics[topic]:
                            del self.topics[topic]
                self.log_event(f"Peer from {peer_ip}, {peer_port} is shutting down! Topics: {topics} deleted.")
            elif action == 'query':
                topic = message.get('topic')
                self.log_event(f"Subscriber querying for Topic: {topic}")
                peers = self.topics.get(topic, [])
                
                if peers:
                    response = json.dumps({'peers': peers}).encode()
                    self.log_event(f"Topic: {topic} found at {peers}")
                else:
                    response = json.dumps({'error': 'Topic not found'}).encode()
                writer.write(response)
                await writer.drain()

        except Exception as e:
            print(f"Error: {str(e)}")

        writer.close()

    async def start(self):
        server = await asyncio.start_server(self.handle_client, self.host, self.port)
        self.log_event(f"Indexing server started on {self.host}, {self.port}")
        print("Waiting for peers to host topics and publish messages...")
        async with server:
            await server.serve_forever()

    def log_event(self, event):
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {event}")

if __name__ == "__main__":
    indexing_server = IndexingServer()
    asyncio.run(indexing_server.start())
