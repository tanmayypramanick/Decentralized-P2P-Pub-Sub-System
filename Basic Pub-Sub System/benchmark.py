import time
import random
import uuid
import matplotlib.pyplot as plt
from client_api import ClientAPI
from tabulate import tabulate

class Benchmark:
    def __init__(self, host='localhost', port=8080):
        self.host = host
        self.port = port
        self.api = ClientAPI(host, port)
        self.results = {}

    # Measure the time taken for a specific operation across multiple clients
    def benchmark_operation(self, operation, num_clients):
        times = []
        for _ in range(num_clients):
            try:
                start_time = time.time()
                operation()
                times.append(time.time() - start_time)
            except Exception as e:
                print(f"Error during operation: {e}")
        return sum(times) / len(times) if times else 0

    # Register publisher and create a unique topic
    def create_topic_operation(self):
        pid = self.api.register_publisher()
        topic = f'topic{uuid.uuid4()}'
        self.api.create_topic(pid, topic)

    # Create and then delete a topic
    def delete_topic_operation(self):
        pid = self.api.register_publisher()
        topic = f'topic{uuid.uuid4()}'
        self.api.create_topic(pid, topic)
        self.api.delete_topic(pid, topic)

    # Register publisher, create a topic, and send a message
    def send_message_operation(self):
        pid = self.api.register_publisher()
        topic = f'topic{uuid.uuid4()}'
        self.api.create_topic(pid, topic)
        self.api.send_message(pid, topic, f'Message {random.randint(1, 1000)}')

    # Register subscriber and subscribe to a topic
    def subscribe_operation(self):
        sid = self.api.register_subscriber()
        topic = f'topic{uuid.uuid4()}'
        self.api.create_topic(sid, topic)
        self.api.subscribe(sid, topic)

    # Send and pull messages for a topic
    def pull_messages_operation(self):
        sid = self.api.register_subscriber()
        pid = self.api.register_publisher()
        topic = f'topic{uuid.uuid4()}'
        self.api.create_topic(pid, topic)
        self.api.subscribe(sid, topic)
        self.api.send_message(pid, topic, f'Test message {random.randint(1, 1000)}')
        self.api.pull_messages(sid, topic)

    # Display message in a box format
    def print_box(self, message):
        print("╔" + "═" * (len(message) + 2) + "╗")
        print(f"║ {message} ║")
        print("╚" + "═" * (len(message) + 2) + "╝")

    # Run all benchmarks
    def run_benchmarks(self):
        max_clients = 50

        self.print_box("Creating topics")
        create_topic_time = self.benchmark_operation(self.create_topic_operation, max_clients)
        self.results['Create Topic'] = create_topic_time

        self.print_box("Deleting topics")
        delete_topic_time = self.benchmark_operation(self.delete_topic_operation, max_clients)
        self.results['Delete Topic'] = delete_topic_time

        self.print_box("Publishing messages to topics")
        send_message_time = self.benchmark_operation(self.send_message_operation, max_clients)
        self.results['Publish Message'] = send_message_time

        self.print_box("Subscribing to topics")
        subscribe_time = self.benchmark_operation(self.subscribe_operation, max_clients)
        self.results['Subscribe'] = subscribe_time

        self.print_box("Pulling messages from topics")
        pull_messages_time = self.benchmark_operation(self.pull_messages_operation, max_clients)
        self.results['Pull Messages'] = pull_messages_time

        self.print_results()
        self.save_results()
        self.plot_results()

    # Display benchmark results in table format
    def print_results(self):
        table = [[operation, f"{time:.6f} seconds"] for operation, time in self.results.items()]
        print("\nBenchmark Results:")
        print(tabulate(table, headers=['Operation', 'Throughput Time'], tablefmt='grid'))

    # Save benchmark results to a file
    def save_results(self):
        with open('benchmark_results.txt', 'w') as f:
            f.write("Benchmark Results:\n")
            f.write(tabulate([[op, f"{time:.6f}"] for op, time in self.results.items()], 
                             headers=['Operation', 'Throughput Time (seconds)'], 
                             tablefmt='grid'))

    # Plot and save results as a bar chart
    def plot_results(self):
        operations = list(self.results.keys())
        times = list(self.results.values())

        plt.figure(figsize=(10, 6))
        plt.bar(operations, times)
        plt.title('Message Broker Benchmark Results')
        plt.xlabel('Operations')
        plt.ylabel('Throughput Time (seconds)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig('benchmark_results.png')
        plt.close()

if __name__ == "__main__":
    benchmark = Benchmark()
    benchmark.run_benchmarks()

