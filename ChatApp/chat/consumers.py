import json
import base64
import uuid
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.files.base import ContentFile
from django.contrib.auth.models import User
from .models import Message, UserProfile, ChatConnection


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.sender = self.scope['url_route']['kwargs']['sender']
        self.recipient = self.scope['url_route']['kwargs']['recipient']
        self.group_name = f'chat_{min(self.sender, self.recipient)}_{max(self.sender, self.recipient)}'

        # Mark sender as online
        await set_user_online(self.sender, True)

        # Notify recipient of sender's online status
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'status_update',
                'user': self.sender,
                'online': True
            }
        )

        # Add to WebSocket group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Mark sender as offline
        await set_user_online(self.sender, False)

        # Notify recipient of sender's offline status
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'status_update',
                'user': self.sender,
                'online': False
            }
        )

        # Remove from WebSocket group
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        image_data = data.get('image', None)
        sender = data['sender']
        recipient = self.recipient

        msg = await save_message_with_image(sender, recipient, message, image_data)

        # Send message to the WebSocket group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender,
                'image_url': msg.image.url if msg.image else '',
            }
        )

        # Optionally, send message read status update after sending
        await self.mark_messages_as_read(sender, recipient)

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        image_url = event.get('image_url', '')

        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'image_url': image_url
        }))

    async def status_update(self, event):
        # Send online/offline status update to WebSocket client
        await self.send(text_data=json.dumps({
            'type': 'status',
            'user': event['user'],
            'online': event['online']
        }))

    @database_sync_to_async
    def mark_messages_as_read(self, sender, recipient):
        # Mark messages as read when recipient receives them
        unread_messages = Message.objects.filter(sender__username=sender, recipient__username=recipient, is_read=False)
        unread_messages.update(is_read=True)


# ------------- HELPER DB FUNCTIONS ------------- #

@database_sync_to_async
def save_message(sender_username, recipient_username, message):
    sender = User.objects.get(username=sender_username)
    recipient = User.objects.get(username=recipient_username)

    # Save message
    msg = Message.objects.create(
        sender=sender,
        recipient=recipient,
        message=message,
        is_read=False
    )

    # Create or update chat connection
    user1, user2 = sorted([sender, recipient], key=lambda u: u.id)
    ChatConnection.objects.update_or_create(
        user1=user1,
        user2=user2,
        defaults={"last_interaction": msg.timestamp}
    )

    return msg


@database_sync_to_async
def save_message_with_image(sender_username, recipient_username, message, image_data):
    sender = User.objects.get(username=sender_username)
    recipient = User.objects.get(username=recipient_username)

    image_file = None
    if image_data:
        try:
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]
            file_name = f"{uuid.uuid4()}.{ext}"
            print(f"Decoded image with extension {ext}")  # <-- Log image extension
            image_file = ContentFile(base64.b64decode(imgstr), name=file_name)
        except Exception as e:
            print("Failed to decode image:", e)

    msg = Message.objects.create(
        sender=sender,
        recipient=recipient,
        message=message,
        image=image_file,
        is_read=False
    )

    # Ensure chat connection exists
    user1, user2 = sorted([sender, recipient], key=lambda u: u.id)
    ChatConnection.objects.update_or_create(
        user1=user1,
        user2=user2,
        defaults={"last_interaction": msg.timestamp}
    )

    return msg


@database_sync_to_async
def set_user_online(username, status=True):
    user = User.objects.get(username=username)
    profile, created = UserProfile.objects.get_or_create(user=user)
    profile.is_online = status
    profile.save()
