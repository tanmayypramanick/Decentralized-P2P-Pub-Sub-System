import asyncio
from client_api import ClientAPI
import time

class Subscriber:
    def __init__(self, indexing_host='127.0.0.1', indexing_port=9090):
        # Client API to connect to the indexing server initially
        self.indexing_api = ClientAPI(indexing_host, indexing_port)

    async def query_indexing_server(self, topic):
        print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Querying about Topic: {topic} from Indexing Server")
        try:
            response = await self.indexing_api.send_and_receive({'action': 'query', 'topic': topic})
            if 'error' in response:
                print(f"Error: {response['error']}")
                return []
            return response.get('peers', [])
        except Exception as e:
            print(f"Error querying indexing server: {str(e)}")
            return []

    async def subscribe_and_pull_messages(self, topic, peer_ip, peer_port):
        try:
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Topic: {topic} found at {peer_ip}, {peer_port}")
            peer_api = ClientAPI(peer_ip, peer_port)
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Subscriber connected to {peer_ip}, {peer_port}")
            
            # Subscribe to the topic
            await peer_api.subscribe(topic)
            print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Subscriber subscribed to topic: {topic}\n")
            
            # Pull messages from the topic
            print(f"Subscriber pulling messages from topic: {topic}")
            messages = await peer_api.pull_messages(topic)
            if messages:
                print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Pulled Messages from Topic: {topic}: {', '.join(messages)}")
            else:
                print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - No messages found in Topic: {topic}")
        except Exception as e:
            print(f"Error subscribing and pulling messages: {str(e)}")

    async def start(self):
        topics = ['Sports', 'TV']  
        
        for topic in topics:
            peers = await self.query_indexing_server(topic)
            if peers:
                for peer_ip, peer_port in peers:
                    await self.subscribe_and_pull_messages(topic, peer_ip, peer_port)
            else:
                print(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Topic {topic} not found on any peer node.")

if __name__ == "__main__":
    subscriber = Subscriber()
    asyncio.run(subscriber.start())
