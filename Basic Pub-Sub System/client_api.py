import socket
import uuid
import json

class ClientAPI:
    def __init__(self, host='localhost', port=8080):
        # Initialize with server details and establish connection
        self.host = host
        self.port = port
        self.client_socket = None
        self.connect()

    def connect(self):
        # Establish a socket connection with the server
        if self.client_socket:
            self.client_socket.close()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.host, self.port))

    def send_and_receive(self, message):
        # Send message to server and receive response
        self.client_socket.send(json.dumps(message).encode('utf-8') + b'\n')
        response = ""
        while '\n' not in response:
            chunk = self.client_socket.recv(1024).decode('utf-8')
            if not chunk:
                raise ConnectionError("Connection closed by server")
            response += chunk
        return json.loads(response.strip())

    def register_publisher(self):
        # Generate and return a unique Publisher ID
        pid = str(uuid.uuid4())
        print(f"Publisher registered with ID: {pid}")
        return pid

    def create_topic(self, pid, topic):
        # Send request to create a new topic
        print(f"Publisher {pid} requested to create topic: {topic}")
        message = {'command': 'CREATE', 'topic': topic}
        return self.send_and_receive(message)
        
    def delete_topic(self, pid, topic):
        # Send request to delete an existing topic
        print(f"Publisher {pid} requested to delete topic: {topic}")
        message = {'command': 'DELETE', 'topic': topic}
        return self.send_and_receive(message)
    
    def send_message(self, pid, topic, message):
        # Send a message to a specific topic
        print(f"Publisher {pid} sent message to topic '{topic}': {message}")
        msg = {'command': 'PUBLISH', 'topic': topic, 'message': message}
        return self.send_and_receive(msg)

    def register_subscriber(self):
        # Generate and return a unique Subscriber ID
        sid = str(uuid.uuid4())
        print(f"Subscriber registered with ID: {sid}")
        return sid

    def subscribe(self, sid, topic):
        # Send request to subscribe to a topic
        print(f"Subscriber {sid} subscribed to topic: {topic}")
        message = {'command': 'SUBSCRIBE', 'topic': topic, 'sid': sid}
        return self.send_and_receive(message)

    def pull_messages(self, sid, topic):
        # Request to pull new messages from a topic
        print(f"Subscriber {sid} pulling messages from topic: {topic}")
        message = {'command': 'PULL', 'topic': topic, 'sid': sid}
        response = self.send_and_receive(message)
        return response.get('messages', [])
