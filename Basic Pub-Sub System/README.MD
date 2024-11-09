# Message Broker System

This project implements a simple publish-subscribe message broker system using Python. It consists of three main components: a Message Broker, Publishers, and Subscribers.

## Components

1. **MessageBroker.py**: The central server that manages topics and message distribution.
2. **publisher.py**: A client that can create topics and publish messages.
3. **subscriber.py**: A client that can subscribe to topics and receive messages.

## Requirements

- Python 3.x
- Socket library (built-in)
- Threading library (built-in)
- Matplotlib library
- Tabulate library
- JSON library
- UUID library
- Random
- Time

## Setup and Running

1. Start the Message Broker: (NEW TERMINAL)

2. Run a Publisher:           (NEW TERMINAL)

3. Run a Subscriber:        (NEW TERMINAL)


## Testing

1. Start the Message Broker: (NEW TERMINAL)

2. Run the Benchmark code:           (NEW TERMINAL)

## Usage

### Publisher
- Creates a topic named 'news'
- Publishes a message to the 'news' topic

### Subscriber
- Subscribes to the 'news' topic
- Continuously listens for and prints received messages

## Features

- Multi-threaded message broker to handle multiple clients
- Simple publish-subscribe model
- Topic-based message routing

## Limitations and Future Improvements

- Currently, all data is stored in memory
- No persistence of messages or topics
- Limited error handling and logging
- Could be extended with more robust features like message queuing, persistence, and scalability improvements


