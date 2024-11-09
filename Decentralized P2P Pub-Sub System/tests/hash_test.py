import time
import hashlib
import random
from collections import defaultdict
import numpy as np

# Set the number of trials for each experiment
NUM_TRIALS = 5
TOPIC_COUNTS = [1000, 5000, 10000, 50000, 100000]  # Varying topic loads for experimentation

def hash_topic(topic):
    """Hash the topic to a 3-bit identifier for node assignment."""
    hash_value = int(hashlib.sha256(topic.encode()).hexdigest(), 16)
    binary_id = hash_value % 8  # Modulo 8 for 3-bit node ID
    return binary_id

def evaluate_time_complexity():
    print("Evaluating time complexity and average time cost...")
    times = []

    for count in TOPIC_COUNTS:
        start_time = time.time()
        for i in range(count):
            topic = f"topic_{i}"
            hash_topic(topic)
        end_time = time.time()
        avg_time = (end_time - start_time) / count
        times.append(avg_time)
        print(f"Topics: {count}, Average time per hash: {avg_time:.10f} seconds")

    print("\nTime complexity experiment completed.")
    return times

def evaluate_distribution():
    print("Evaluating even distribution of topics across nodes...")
    
    results = {}
    
    for count in TOPIC_COUNTS:
        distribution = defaultdict(int)
        for i in range(count):
            topic = f"topic_{random.randint(0, 10**6)}"
            node_id = hash_topic(topic)
            distribution[node_id] += 1

        # Analyze distribution
        counts = list(distribution.values())
        avg_topics = np.mean(counts)
        max_topics = max(counts)
        min_topics = min(counts)
        range_diff = max_topics - min_topics

        results[count] = {
            'avg_topics': avg_topics,
            'max_topics': max_topics,
            'min_topics': min_topics,
            'range_diff': range_diff
        }
        
        print(f"\nTopic count: {count}")
        print(f"Average topics per node: {avg_topics}")
        print(f"Max topics on a single node: {max_topics}")
        print(f"Min topics on a single node: {min_topics}")
        print(f"Range of topics distribution (max - min): {range_diff}")

    print("\nDistribution experiment completed.")
    return results

if __name__ == "__main__":
    # Run both experiments
    time_complexity_results = evaluate_time_complexity()
    distribution_results = evaluate_distribution()
