import asyncio
import argparse
from client_api import ClientAPI
import time

class Publisher:
    def __init__(self, peer_host, peer_port, indexing_host="127.0.0.1", indexing_port=9090):
        self.api = ClientAPI(peer_host, peer_port)
        self.indexing_api = ClientAPI(indexing_host, indexing_port)
        self.peer_host = peer_host  
        self.peer_port = peer_port

    async def notify_indexing_server(self, action, topics, deleted_topics=None):
        try:
            if deleted_topics:
                message = {
                    'action': 'topic_delete',
                    'topics': deleted_topics,
                    'peer_ip': self.peer_host,  
                    'peer_port': self.peer_port
                }
                print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Notifying indexing server about deleted topics: {deleted_topics}")
                await self.indexing_api.send_and_receive(message)
            else:
                message = {
                    'action': action,
                    'topics': topics,
                    'peer_ip': self.peer_host,  
                    'peer_port': self.peer_port
                }
                print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Notifying indexing server about topics: {topics}")
                await self.indexing_api.send_and_receive(message)
        except Exception as e:
            print(f"Error sending message to indexing server: {str(e)}")

    async def start(self):
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Publisher started on {self.api.host}, {self.api.port}")
        
        # Create topics
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Creating topic: Music")
        await self.api.create_topic('Music')
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Creating topic: TV")
        await self.api.create_topic('TV')
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Creating topic: Movie")
        await self.api.create_topic('Movie')

        # Notify the indexing server about the created topics
        await self.notify_indexing_server('topic_update', ['Music', 'TV', 'Movie'])

        # Send messages to the topics
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Publishing message to topic 'Music': New Album Launched!")
        await self.api.send_message('Music', "New Album Launched!")
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Publishing message to topic 'TV': BiggBoss Season 18 will start soon.")
        await self.api.send_message('TV', "BiggBoss Season 18 will start soon.")
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Publishing message to topic 'Movie': New movie released!")
        await self.api.send_message('Movie', "New movie released!")
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Publishing message to topic 'TV': IIFA Awards event announced.")
        await self.api.send_message('TV', "IIFA Awards event announced.")

        # Delete 'Entertainment' topic
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Deleting topic: Movie")
        await self.api.delete_topic('Movie')

        # Notify the indexing server that the 'Entertainment' topic was deleted
        await self.notify_indexing_server('topic_delete', [], deleted_topics=['Movie'])

if __name__ == "__main__":
    # Argument parser for dynamic peer IP and port specification
    parser = argparse.ArgumentParser(description="Publisher Configuration")
    parser.add_argument("--peer-ip", type=str, default="127.0.0.1", help="IP address of the Peer Node")
    parser.add_argument("--peer-port", type=int, default=8081, help="Port of the Peer Node")

    args = parser.parse_args()

    # Validate that the peer IP is not 0.0.0.0
    if args.peer_ip == "0.0.0.0":
        print("Error: You cannot connect to '0.0.0.0'. Use a valid IP address like '127.0.0.1'.")
        exit(1)

    # Initialize the publisher with command-line arguments
    publisher = Publisher(args.peer_ip, args.peer_port)
    asyncio.run(publisher.start())
