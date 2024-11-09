import asyncio
import sys
from client_api import ClientAPI
from dht_hash import hash_topic

class Publisher:
    def __init__(self, node_id):
        self.api = ClientAPI(node_id)
        self.node_id = node_id

    async def start(self):
        # list for topics
        topics = ["News", "Sports", "Entertainment"]

        # Separate dictionary for messages corresponding to each topic
        messages = {
            "News": "Breaking news just in!",
            "Sports": "Live sports event tonight!",
            "Entertainment": "New movie release this Friday!"
        }

        # Create and publish messages to each topic
        for topic in topics:
            target_node = hash_topic(topic)  # Determine the correct node based on the hash of the topic

            print(f"Publisher ({self.node_id}): Creating topic '{topic}' on target node '{target_node}'")
            await self.api.create_topic(topic)
            print(f"Publisher ({self.node_id}): Created topic '{topic}' on node '{target_node}'")

            # Publish the predefined message to the topic
            message = messages.get(topic, f"Default message for {topic}")
            print(f"Publisher ({self.node_id}): Publishing message to '{topic}' on node '{target_node}': {message}")
            await self.api.send_message(topic, message)
            print(f"Publisher ({self.node_id}): Published message to '{topic}'")

        # Specify a topic for deletion
        delete_topic = "Entertainment"
        delete_target_node = hash_topic(delete_topic)
        
        print(f"Publisher ({self.node_id}): Deleting topic '{delete_topic}' from target node '{delete_target_node}'")
        await self.api.delete_topic(delete_topic)
        print(f"Publisher ({self.node_id}): Deleted topic '{delete_topic}' from node '{delete_target_node}'")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python publisher.py <node_id>")
        sys.exit(1)

    node_id = sys.argv[1]
    publisher = Publisher(node_id)
    asyncio.run(publisher.start())
