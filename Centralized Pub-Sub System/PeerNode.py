import asyncio
import argparse
import socket
import signal
import sys
import time
from client_api import ClientAPI
from PeerServer import PeerServer

class PeerNode:
    def __init__(self, peer_ip, peer_port, indexing_host="127.0.0.1", indexing_port=9090):
        self.peer_ip = peer_ip
        self.peer_port = peer_port
        self.indexing_host = indexing_host
        self.indexing_port = indexing_port
        self.peer_server = PeerServer(peer_ip, peer_port)
        self.api = ClientAPI(self.indexing_host, self.indexing_port)

    async def register_with_indexing_server(self):
        if self.peer_ip == '0.0.0.0':
            self.peer_ip = self.resolve_local_ip()

        await self.api.send_and_receive({
            'action': 'register',
            'peer_ip': self.peer_ip,
            'peer_port': self.peer_port
        })

    async def unregister_from_indexing_server(self):
        # Notify the indexing server that the peer is shutting down
        topics = list(self.peer_server.topics.keys())  
        if topics:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Unregistering peer and deleting topics: {topics}")
            await self.api.send_and_receive({
                'action': 'unregister',
                'peer_ip': self.peer_ip,
                'peer_port': self.peer_port,
                'topics': topics
            })
        else:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - No topics to unregister for peer {self.peer_ip}:{self.peer_port}")

    def resolve_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            local_ip = s.getsockname()[0]
        except Exception as e:
            print(f"Error resolving local IP: {str(e)}")
            local_ip = '127.0.0.1'
        finally:
            s.close()
        return local_ip

    async def start(self):
        await asyncio.gather(
            self.peer_server.start(),
            self.register_with_indexing_server()
        )

    def handle_shutdown(self, signal, frame):
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Received shutdown signal, unregistering peer from Indexing Server...")
        loop = asyncio.get_event_loop()

        # Schedule the unregister coroutine and stop the event loop after it's done
        loop.create_task(self.unregister_from_indexing_server())
        loop.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PeerNode Configuration")
    parser.add_argument("--peer-ip", type=str, default="127.0.0.1", help="IP address of the Peer Node")
    parser.add_argument("--peer-port", type=int, default=8081, help="Port of the Peer Node")
    args = parser.parse_args()

    peer_node = PeerNode(args.peer_ip, args.peer_port)

    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, peer_node.handle_shutdown)  # Ctrl+C
    signal.signal(signal.SIGTERM, peer_node.handle_shutdown)  # Termination signal

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(peer_node.start())
    finally:
        loop.run_forever()
        loop.close()
