import socket
import threading
import json

class MessageBroker:
    def __init__(self, host='localhost', port=8080):
        # Initialize server and data structures
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(5)
        self.topics = {}
        self.subscribers = {}
        self.subscriber_views = {}
        self.lock = threading.Lock()

    def handle_client(self, client_socket):
        # Handle incoming client messages
        try:
            while True:
                message = client_socket.recv(1024).decode('utf-8').strip()
                if not message:
                    break
                data = json.loads(message)
                command = data.get('command')
                topic = data.get('topic')
                msg = data.get('message')
                sid = data.get('sid')

                # Handle different client commands
                if command == 'CREATE' and topic:
                    self.create_topic(topic)
                elif command == 'PUBLISH' and topic and msg:
                    self.publish(topic, msg)
                elif command == 'SUBSCRIBE' and topic and sid:
                    self.subscribe(sid, topic)
                elif command == 'PULL' and topic and sid:
                    self.pull_messages(client_socket, sid, topic)
                else:
                    print(f"Invalid command: {message}")

                client_socket.send(json.dumps({"status": "ok"}).encode('utf-8') + b'\n')
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()

    def create_topic(self, topic):
        # Create a new topic
        with self.lock:
            if topic not in self.topics:
                self.topics[topic] = []
                self.subscriber_views[topic] = 0
                print(f"Topic '{topic}' created.")
                
    def delete_topic(self, topic):
        # Delete an existing topic
        with self.lock:
            if topic in self.topics:
                del self.topics[topic]
                print(f"Topic '{topic}' deleted.")

    def publish(self, topic, message):
        # Publish a message to a topic
        with self.lock:
            if topic in self.topics:
                self.topics[topic].append(message)
                print(f"Message published to topic '{topic}': {message}")

    def subscribe(self, sid, topic):
        # Subscribe a client to a topic
        with self.lock:
            if topic not in self.topics:
                self.create_topic(topic)
            if sid not in self.subscribers:
                self.subscribers[sid] = {'subscriptions': []}
            if topic not in self.subscribers[sid]['subscriptions']:
                self.subscribers[sid]['subscriptions'].append(topic)
            print(f"Client {sid} subscribed to topic '{topic}'.")

    def pull_messages(self, client_socket, sid, topic):
        # Send pulled messages to a subscriber
        with self.lock:
            if topic in self.subscribers[sid]['subscriptions']:
                messages = self.topics.get(topic, []).copy()
                self.subscriber_views[topic] += 1
                # Reset topic if all subscribers have pulled messages
                if self.subscriber_views[topic] >= len([s for s in self.subscribers if topic in self.subscribers[s]['subscriptions']]):
                    self.topics[topic] = []
                    self.subscriber_views[topic] = 0
                response = json.dumps({"messages": messages})
            else:
                response = json.dumps({"messages": []})
            client_socket.send(response.encode('utf-8') + b'\n')

    def start(self):
        # Start the message broker server
        print("Message Broker started...")
        while True:
            client_socket, addr = self.server.accept()
            print(f"Accepted connection from {addr}")
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_handler.start()

if __name__ == "__main__":
    broker = MessageBroker()
    broker.start()

