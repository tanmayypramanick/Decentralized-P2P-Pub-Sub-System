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
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Creating topic: News")
        await self.api.create_topic('News')
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Creating topic: Sports")
        await self.api.create_topic('Sports')
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Creating topic: Entertainment")
        await self.api.create_topic('Entertainment')

        # Notify the indexing server about the created topics
        await self.notify_indexing_server('topic_update', ['News', 'Sports', 'Entertainment'])

        # Send messages to the topics
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Publishing message to topic 'News': Breaking news!")
        await self.api.send_message('News', "Breaking news!")
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Publishing message to topic 'Sports': Sports event happening today.")
        await self.api.send_message('Sports', "Sports event happening today.")
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Publishing message to topic 'Entertainment': New movie released!")
        await self.api.send_message('Entertainment', "New movie released!")
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Publishing message to topic 'Sports': Another sports event announced.")
        await self.api.send_message('Sports', "Another sports event announced.")

        # Delete 'Entertainment' topic
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Deleting topic: Entertainment")
        await self.api.delete_topic('Entertainment')

        # Notify the indexing server that the 'Entertainment' topic was deleted
        await self.notify_indexing_server('topic_delete', [], deleted_topics=['Entertainment'])

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
