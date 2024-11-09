import asyncio
import argparse
from client_api import ClientAPI
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Subscriber:
    def __init__(self, peer_id):
        self.api = ClientAPI(peer_id)

    async def start(self):
        topics = ['News', 'Sports', 'Entertainment', 'Music']

        for topic in topics:
            logging.info(f"[Subscriber] Attempting to subscribe to topic: '{topic}'")
            subscribe_response = await self.api.subscribe(topic)

            # Only proceed with pulling messages if subscription was successful
            if subscribe_response.get("status") == "Subscribed":
                logging.info(f"[Subscriber] Pulling messages for topic: '{topic}'")
                messages = await self.api.pull_messages(topic)
                if messages:
                    for msg in messages:
                        logging.info(f"[Subscriber] Message on topic '{topic}': {msg}")
                else:
                    logging.info(f"[Subscriber] No messages available for topic '{topic}'")
            else:
                logging.info(f"[Subscriber] Topic '{topic}' does not exist or is unavailable")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Subscriber Configuration")
    parser.add_argument("peer_id", type=str, help="ID of the Peer Node to connect to (e.g., 000)")
    args = parser.parse_args()

    subscriber = Subscriber(args.peer_id)
    asyncio.run(subscriber.start())
