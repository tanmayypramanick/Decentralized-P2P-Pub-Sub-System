# P2P Topic Publisher-Subscriber System

## Overview

Welcome to the P2P Topic Publisher-Subscriber System! This project is a simple peer-to-peer (P2P) implementation of a topic-based publisher-subscriber system that consists of multiple peer nodes and a central indexing server.

- **Indexing Server:** Manages the list of active peer nodes and the topics they host.
- **Peer Nodes:** Each peer node can host topics and serve as a publisher or subscriber for these topics.
- **Publisher and Subscriber:** Allows users to publish messages to topics and subscribe to topics to receive messages.

## Program Structure

```
- Section01_Pramanick_Tanmay_PA2/
  
  - IndexingServer.py
  - PeerNode.py
  - PeerServer.py
  - client_api.py
  - Publisher.py
  - Publisher2.py
  - Subscriber.py

  - tests/
      - test_deployment.py
      - test_performance.py
      - test_100k_topics.py
      - benchmark_create_topic.py
      - benchmark_delete_topic.py
      - benchmark_send_message.py
      - benchmark_subscribe.py
      - benchmark_pull_message.py
      - graphs/
          - All screenshots of the test output (graphs)
      - data/
          - all benchmarks in csv format
        
  - Docs/
    - Report.pdf
    - Design_Document.pdf
  - README.md
  - requirements.txt
```

## Requirements

Please ensure that you have all the required dependencies installed. To install the dependencies, run:

```sh
pip install -r requirements.txt
```

## Running the System

To successfully run the P2P Topic Publisher-Subscriber System, follow these detailed steps. Each step should be run in a separate terminal window:

### 1. Start the Indexing Server

The indexing server is the central component that keeps track of all peer nodes and the topics they hold. To start the indexing server, open a new terminal window and run:

```sh
python IndexingServer.py
```

### 2. Start Peer Nodes

You need to run multiple peer nodes, each in a separate terminal window. Each peer node hosts its own topics and interacts with publishers and subscribers. To start a peer node, open a new terminal window for each peer and run: 

In this case you can run 2 of them, as I have created 2 publisher clients.

```sh
python PeerNode.py --peer-ip 0.0.0.0 --peer-port <peer-port>
```

Replace `<peer-port>` with a unique port number for each peer, e.g., 8000, 8001, 8002, etc.


### 3. Start Publisher Clients

To create topics and publish messages to that topic, you need to start a publisher client. For each publisher, open a new terminal window and run:

```sh
python Publisher.py --peer-ip 0.0.0.0 --peer-port <peer-port>
```
Replace `<peer-port>` with a unique port number for each peer, e.g., 8000, 8001, 8002, etc. ( SAME AS ONE OF THE PEER NODE )

```sh
python Publisher2.py --peer-ip 0.0.0.0 --peer-port <peer-port>
```
Replace `<peer-port>` with a unique port number for each peer, e.g., 8000, 8001, 8002, etc. ( SAME AS ONE OF THE PEER NODE )

### 4. Start Subscriber Clients

Subscribers can subscribe to topics and pull messages. For each subscriber, open a new terminal window and run:

```sh
python Subscriber.py
```

Once subscribed, subscribers will start receiving messages published to the topic.

### Communication Flow

1. **Indexing Server** starts and waits for peers to register.
2. **Peer Nodes** register themselves with the **Indexing Server**, specifying which topics they host.
3. **Publisher Clients** creates topics and publish messages to topics hosted by specific peer nodes.
4. **Subscriber Clients** subscribe to topics and pull messages from the corresponding peer nodes.

### Example Workflow

1. Start the **Indexing Server** in Terminal 1.
2. Start **Peer Node 1** on some port in Terminal 2.
3. Start **Peer Node 2** on a different port in Terminal 3.
4. Start both **Publisher** in Terminal 4 and 5 to create topic and publish messages to a topic hosted by Peer Node 1 and 2.
5. Start a **Subscriber** in Terminal 6 to subscribe to the same topic and receive messages.

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
- **Send Message:** `benchmark_send_message.py`
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

- **Multiple Terminals:** For each component (indexing server, peer node, publisher, subscriber), you need to open a new terminal window.
- **Unique Ports:** Each peer node should use a unique port to avoid conflicts.
- **Order of Execution:** Start the indexing server first, followed by peer nodes, and then publisher/subscriber clients.

## Troubleshooting

- If you encounter errors when starting a peer node, ensure the port is not already in use.
- Make sure to start the indexing server before starting any peer nodes or clients.

## Author
- Tanmay Pramanick - A20541164

