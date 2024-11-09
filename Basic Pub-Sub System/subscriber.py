from client_api import ClientAPI

def main():
    # Create API instance and register as a subscriber
    api = ClientAPI()
    sid = api.register_subscriber()
    
    topics = ['News']
    
    # Subscribe to specified topics
    for topic in topics:
        api.subscribe(sid, topic)
        print(f"Subscribed to topic: {topic}")

    # Pull and display messages from subscribed topics
    for topic in topics:
        print(f"Pulling messages from topic: {topic}")
        messages = api.pull_messages(sid, topic)
        if messages:
            print(f"Messages from {topic}:")
            for msg in messages:
                print(f"  - {msg}")
        else:
            print(f"No new messages for topic '{topic}'.")

if __name__ == "__main__":
    main()
