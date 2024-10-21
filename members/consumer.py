# memebers/consumers.py

from channels.generic.websocket import AsyncWebsocketConsumer
import json

class YourConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Accept the connection
        await self.accept()

    async def disconnect(self, close_code):
        # Do any cleanup on disconnect
        pass

    async def receive(self, text_data):
        # Receive message from WebSocket
        data = json.loads(text_data)
        message = data['message']

        # Send message back to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))
