import asyncio
import json
import time
import socket

class PeerServer:
    def __init__(self, peer_ip, peer_port):  
        self.peer_ip = peer_ip  
        self.peer_port = peer_port
        self.topics = {}

    async def handle_peer(self, reader, writer):
        try:
            data = await reader.read(100)
            message = json.loads(data.decode())
            command = message.get('command')

            if command == 'CREATE':
                topic = message.get('topic')
                self.topics[topic] = []
                self.log_event(f"Topic Created: {topic}")
            elif command == 'PUBLISH':
                topic = message.get('topic')
                msg = message.get('message')
                if topic in self.topics:
                    self.topics[topic].append(msg)
                    self.log_event(f"Publisher sent message to topic '{topic}': {msg}")
                else:
                    self.log_event(f"Error: Topic '{topic}' not found.")
            elif command == 'SUBSCRIBE':
                topic = message.get('topic')
                self.log_event(f"Subscriber subscribed to topic: {topic}")
            elif command == 'PULL':
                topic = message.get('topic')
                if topic in self.topics:
                    messages = self.topics.get(topic, [])
                    response = {'messages': messages}
                    writer.write(json.dumps(response).encode())
                    await writer.drain()
                    self.log_event(f"Subscriber pulled messages from topic '{topic}': {', '.join(messages)}")
                else:
                    self.log_event(f"Error: Topic '{topic}' not found.")
                    writer.write(json.dumps({'error': 'Topic not found'}).encode())
                    await writer.drain()
            elif command == 'DELETE':
                topic = message.get('topic')
                if topic in self.topics:
                    del self.topics[topic]
                    self.log_event(f"Topic Deleted: {topic}")
                else:
                    self.log_event(f"Error: Topic '{topic}' not found.")
        except Exception as e:
            self.log_event(f"Error handling peer request: {str(e)}")
        finally:
            writer.close()

    def resolve_local_ip(self):
        
        try:
            # Connect to a public IP address to figure out the local network IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))  # Google's public DNS server IP
                local_ip = s.getsockname()[0]
        except Exception:
            local_ip = "127.0.0.1"  # Fallback to localhost if the above fails
        return local_ip

    async def start(self):
        try:
            server = await asyncio.start_server(self.handle_peer, self.peer_ip, self.peer_port)

            # If using '0.0.0.0', resolve the actual IP address for logging
            if self.peer_ip == "0.0.0.0":
                resolved_ip = self.resolve_local_ip()
            else:
                resolved_ip = self.peer_ip

            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - PeerServer started on {resolved_ip}, {self.peer_port}")
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Waiting for publishing/subscribing...")

            async with server:
                await server.serve_forever()
        except OSError as e:
            if e.errno == 10048:
                print(f"Error: Could not bind to IP {self.peer_ip} on port {self.peer_port}. Port might already be in use.")
            else:
                print(f"Error: {e}")

    def log_event(self, event):
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {event}")

if __name__ == "__main__":
    peer_server = PeerServer('127.0.0.1', 8081)
    asyncio.run(peer_server.start())
