# 🛠️ Decentralized P2P Pub-Sub System Repository

Welcome to the **Decentralized P2P Pub-Sub System** repository! This project showcases different stages of developing a publisher-subscriber system, focusing on distributed systems. Each folder in this repository represents one stage of the system's evolution, starting from a basic setup and advancing to a fully decentralized peer-to-peer (P2P) implementation.

## 📝 Overview of the Repository
This repository contains three main folders, each representing different assignments:

1. **Basic Pub-Sub System** 
2. **Centralized P2P Pub-Sub System** 
3. **Decentralized P2P Pub-Sub System** 

Each folder has its own README file with detailed instructions on how to run that specific part of the project. Below, you'll find a brief description of each assignment and its functionality.

## 📑 Project Structure
```
- Decentralized P2P Pub-Sub System/
  - Basic Pub-Sub System/
    - (All files related)
    - README.md
  
  - Centralized P2P Pub-Sub System/
    - (All files related)
    - README.md
  
  - Decentralized P2P Pub-Sub System/
    - (All files related)
    - README.md
  
  - README.md  ✉️ (This file)
```

## 🛠️ Basic Pub-Sub System

The **Basic Pub-Sub System** folder contains a straightforward implementation of a publisher-subscriber pattern. In this version:

- **Topics** are hosted by a central server.
- **Publishers** can create topics and publish messages.
- **Subscribers** can subscribe to topics and receive messages.

### Features
- Basic communication between publishers and subscribers.
- A single server to manage all topics and subscriptions.

### Running Instructions
For detailed steps to run the project, refer to the README file inside the **Basic Pub-Sub System** folder.

---

## 🔗 Centralized P2P Pub-Sub System

The **Centralized P2P Pub-Sub System** is an extension of the basic system, introducing the concept of peer nodes. The main highlights of this implementation include:

- **Indexing Server** that acts as the central manager for topics and peer nodes.
- **Peer Nodes** can register themselves, host topics, and facilitate message exchange between publishers and subscribers.
- **Publishers** and **Subscribers** connect to specific peer nodes to interact with topics.

### Features
- A central server to manage nodes and topics.
- Multiple peers can host topics, allowing publishers and subscribers to interact with different nodes.
- A more distributed architecture compared to Assignment 1.

### Running Instructions
Refer to the README inside the **Centralized P2P Pub-Sub System** folder for setup and usage instructions.

---

## 🛠️ Decentralized P2P Pub-Sub System

The **Decentralized P2P Pub-Sub System** represents the final stage of this project. The central indexing server has been removed, and the system now operates in a fully **decentralized** manner using a **Distributed Hash Table (DHT)** for topic management.

- **Hypercube Network Topology**: Peer nodes are connected based on a hypercube structure to facilitate efficient routing of requests.
- **Distributed Hash Table (DHT)**: Topics are distributed across peer nodes without any central coordination, ensuring a highly distributed architecture.
- **Fault Tolerance and Scalability**: Nodes operate independently, making the system more fault-tolerant and scalable.

### Features
- Fully decentralized topic management using DHT.
- Each peer stores a portion of the DHT, and nodes only communicate with their neighbors.
- Increased scalability and resilience.

### Running Instructions
For more information on how to run the **Decentralized P2P Pub-Sub System**, refer to the README file inside its respective folder.

---

## 📊 Summary of Experiments and Benchmarks

Each of these systems includes benchmarks and experiments to evaluate their efficiency, response time, fault tolerance, and performance under different conditions. The benchmarks were conducted to:
- Measure **latency** and **throughput** of different system configurations.
- Test **resilience** to node failures in decentralized networks.
- Evaluate **hash function** performance for topic distribution in the decentralized system.

Graphs and reports for these experiments are provided in the `tests/` and `graphs/` folders within each assignment.

## 🛠️ Installation Requirements
Before running any of the assignments, ensure you have installed the necessary Python packages:

```sh
pip install -r requirements.txt
```

Make sure you run this command for each assignment folder to ensure all dependencies are installed.

## 📈 Getting Started
To get started, clone the repository and navigate to the desired assignment folder. Follow the detailed instructions provided in the respective README file to run the indexing server, peer nodes, publishers, and subscribers.

### Example
```sh
git clone https://github.com/your_username/Decentralized-P2P-Pub-Sub-System.git
cd Decentralized-P2P-Pub-Sub-System/Basic\ Pub-Sub\ System/
python IndexingServer.py
```

## 📄 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## 👨‍💻 Author
- **Tanmay Pramanick**

Feel free to open issues and make contributions to improve this repository! 🎉
