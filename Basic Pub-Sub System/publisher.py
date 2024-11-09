from client_api import ClientAPI

def main():
    # Create API instance and register as a publisher
    api = ClientAPI()
    pid = api.register_publisher()

    topics = ['News', 'Sports', 'Technology', 'Health', 'Entertainment']
    
    # Sample messages for each topic
    messages = {
        'News': [
            'Breaking: Major event happening!',
            'Local news update: City council meets today.',
            'Weather alert: Heavy rain expected tomorrow.'
        ],
        'Sports': [
            'Real Madrid wins the championship!',
            'Ronaldo breaks record for most goals in a season.',
            'Upcoming match: Team FCB vs Team RM this weekend.'
        ],
        'Technology': [
            'AI is changing the world!',
            'New smartphone release with innovative features.',
            'Cybersecurity: Best practices for users.'
        ],
        'Health': [
            'Healthy eating tips for better living.',
            'The importance of regular exercise.',
            'Mental health awareness: Break the stigma.'
        ],
        'Entertainment': [
            'Upcoming blockbuster movie hits theaters.',
            'New album release: Artist Y takes the music world by storm.',
            'TV show finale leaves fans wanting more.'
        ],
    }

    # Create topics
    for topic in topics:
        api.create_topic(pid, topic)

    # Delete specific topics
    topics_to_delete = ['Health', 'Entertainment']
    for topic in topics_to_delete:
        api.delete_topic(pid, topic)

    # Publish messages to remaining topics
    remaining_topics = [topic for topic in topics if topic not in topics_to_delete]
    for topic in remaining_topics:
        if topic in messages:
            for message in messages[topic]:
                api.send_message(pid, topic, message)

    print("Publisher operations completed successfully.")

if __name__ == "__main__":
    main()
