import asyncio
import json

class ClientAPI:
    def __init__(self, host='localhost', port=8081):
        self.host = host
        self.port = port

    async def send_and_receive(self, message):
        reader, writer = await asyncio.open_connection(self.host, self.port)
        writer.write(json.dumps(message).encode('utf-8'))
        await writer.drain()

        data = await reader.read(1024)
        if data:
            response = json.loads(data.decode('utf-8'))
        else:
            response = {}
        writer.close()
        await writer.wait_closed()
        return response

    async def create_topic(self, topic):
        message = {'command': 'CREATE', 'topic': topic}
        return await self.send_and_receive(message)

    async def send_message(self, topic, message):
        msg = {'command': 'PUBLISH', 'topic': topic, 'message': message}
        return await self.send_and_receive(msg)

    async def delete_topic(self, topic):
        message = {'command': 'DELETE', 'topic': topic}
        return await self.send_and_receive(message)

    async def subscribe(self, topic):
        message = {'command': 'SUBSCRIBE', 'topic': topic}
        return await self.send_and_receive(message)

    async def pull_messages(self, topic):
        message = {'command': 'PULL', 'topic': topic}
        response = await self.send_and_receive(message)
        return response.get('messages', [])