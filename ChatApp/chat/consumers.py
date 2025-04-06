import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        sender = self.scope['url_route']['kwargs']['sender']
        recipient = self.scope['url_route']['kwargs']['recipient']

        # Store sender and recipient in the consumer for easy access
        self.sender = sender
        self.recipient = recipient

        # Define the group name using sorted sender and recipient for consistency
        self.group_name = f'chat_{min(sender, recipient)}_{max(sender, recipient)}'

        # Join the group
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group when disconnecting
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Receive message from WebSocket (sender sending the message)
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender = data['sender']

        print(f"Received message from {sender}: {message}")

        # Send the message to the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender,
            }
        )

    # Receive message from group (to send to WebSocket)
    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))
