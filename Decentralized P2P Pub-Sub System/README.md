#  Decentralized P2P System with Distributed Hash Table (DHT) - Assignment 3

## Overview

Welcome to the Decentralized P2P System with DHT! This project is an extension of a peer-to-peer (P2P) implementation that utilizes a Distributed Hash Table (DHT) and a hypercube network topology. This fully decentralized system has the following key components:

- **Peer Nodes:** Each node is independent and manages a unique, non-overlapping portion of the DHT. Peer nodes work together to maintain a consistent view of topics and message storage.
- **Publisher and Subscriber:** Publishers can create topics and publish messages to those topics. Subscribers can subscribe to topics and pull messages.

This assignment builds upon Assignment 2 by removing the central indexing server and adopting a decentralized architecture where all nodes are interconnected.

## Program Structure

```
- Section01_Pramanick_Tanmay_PA3/
  
  - peer_node.py
  - start_all_nodes.py
  - dht_hash.py
  - hypercube.py
  - client_api.py
  - publisher.py
  - publisher2.py
  - subscriber.py

  - tests/
      - hash_test.py
      - hash_comparison.py
      - forwarding_test.py
      - network_test.py
      - benchmark_create_topic.py
      - benchmark_delete_topic.py
      - benchmark_publish_message.py
      - benchmark_subscribe.py
      - benchmark_pull_message.py
      - graphs/
          - All screenshots of the test output (graphs)
      - data/
          - all benchmarks in csv format
        
  - Docs/
    - Report.pdf
    - Design_Document.pdf
    - README.MD
  
  - requirements.txt
```

## Requirements

Please ensure that you have all the required dependencies installed. To install the dependencies, run:

```sh
pip install -r requirements.txt
```

## Running the System

To successfully run the Decentralized P2P Topic Publisher-Subscriber System, follow these detailed steps. Each step should be run in a separate terminal window:

### 1. Start all the Peer Nodes

To start all the Peer Nodes, open a new terminal window and run:

```sh
python start_all_nodes.py
```


### 2. Start Publisher Clients

To create topics and publish messages to that topic, you need to start a publisher client. For each publisher, open a new terminal window and run:

```sh
python publisher.py <node_id>
```
Replace `<node_id>` with a unique port id for each peer, e.g., 000, 001, 010, 011, 100, 101, 110, 111

```sh
python publisher2.py <node_id>
```
Replace `<node_id>` with a unique port id for each peer, e.g., 000, 001, 010, 011, 100, 101, 110, 111

### 4. Start Subscriber Clients

Subscribers can subscribe to topics and pull messages. For each subscriber, open a new terminal window and run:

```sh
python subscriber.py <node_id>
```
Replace `<node_id>` with a unique port id for each peer, e.g., 000, 001, 010, 011, 100, 101, 110, 111

Once subscribed, subscribers will start receiving messages published to the topic.

### Communication Flow

1. **Peer Nodes** form a distributed network without central coordination, collectively managing the DHT.
2. **Publishers** create topics and publish messages, which are stored on specific nodes as determined by the hash of each topic.
3. **Subscribers** subscribe to topics and pull messages, retrieving data from the corresponding nodes.

### Example Workflow

1. Start the **start_all_nodes.py** in Terminal 1.
2. Start **publisher.py** with some ID in Terminal 2.
3. Start **publisher2.py** with some ID in Terminal 3.
4. Start **Subscriber.py** with some ID in Terminal 4 to subscribe to the same topic and receive messages.

## Running Tests and Benchmarks

The tests for evaluating the system are located in the `tests/` folder. The tests measure latency, throughput, and average response times for different configurations and loads.

### Benchmarking Create Topic API

To benchmark the create topic API, run:

```sh
python tests/benchmark_create_topic.py
```

This script will automatically start and stop the peer nodes and measure the throughput and latency for creating topics.

### Benchmarking Other APIs

You can similarly run benchmarks for other APIs:

- **Delete Topic:** `benchmark_delete_topic.py`
- **Publish Message:** `benchmark_publish_message.py`
- **Subscribe:** `benchmark_subscribe.py`
- **Pull Messages:** `benchmark_pull_message.py`

Each of these scripts will output results and generate graphs showing performance metrics.

## Graphical Analysis

The benchmarking scripts generate graphs showing:

- **Throughput vs. Number of Peers:** How throughput changes with the number of peer nodes.
- **Latency vs. Number of Peers:** How latency changes with the number of peer nodes.

These graphs are saved in the `graphs/` folder after running the benchmark scripts.

## Compilation in Linux Environment

This code has been tested to run in a Linux environment using Python 3. Ensure you have installed all dependencies from `requirements.txt` before running the program.

## Important Notes

- **Multiple Terminals:** For each component (peer node, publisher, subscriber), you need to open a new terminal window.
- **Unique Binary Node ID:** Each peer node should use a unique port to avoid conflicts.

## Troubleshooting

- If you encounter errors when starting a peer node, ensure the port is not already in use.
- Make sure to start all 8 Peer Nodes before starting any clients.

## Author
- Tanmay Pramanick - A20541164

