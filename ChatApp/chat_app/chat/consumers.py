import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Message
from django.db.models import Q  # <-- Added Q import here


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.other_username = self.scope['url_route']['kwargs']['username']

        # Validate users
        if not await self.validate_users():
            await self.close()
            return

        # Create consistent room name
        self.room_name = self.get_room_name()
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Send message history
        await self.send_message_history()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'chat_message':
                await self.handle_chat_message(data)
            elif message_type == 'typing':
                await self.handle_typing_indicator(data)
            elif message_type == 'read_receipt':
                await self.handle_read_receipt(data)

        except json.JSONDecodeError as e:
            print("JSON decode error:", e)
        except Exception as e:
            print("Error processing message:", e)

    async def handle_chat_message(self, data):
        message_content = data.get('message', '').strip()
        if not message_content:
            return

        # Save message to database
        message = await self.save_message(message_content)

        # Broadcast message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message.content,
                'sender': self.user.username,
                'timestamp': message.timestamp.isoformat(),
                'message_id': message.id
            }
        )

    async def handle_typing_indicator(self, data):
        is_typing = data.get('typing', False)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'typing': is_typing,
                'sender': self.user.username
            }
        )

    async def handle_read_receipt(self, data):
        message_id = data.get('message_id')
        if message_id:
            await self.mark_message_as_read(message_id)

    async def chat_message(self, event):
        """Send chat message to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender': event['sender'],
            'timestamp': event['timestamp'],
            'message_id': event['message_id']
        }))

    async def typing_indicator(self, event):
        """Send typing status to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'typing_indicator',
            'typing': event['typing'],
            'sender': event['sender']
        }))

    async def send_message_history(self):
        """Send last 50 messages when user connects"""
        messages = await self.get_message_history()
        await self.send(text_data=json.dumps({
            'type': 'message_history',
            'messages': messages
        }))

    # Database operations

    @database_sync_to_async
    def validate_users(self):
        """Validate both users exist and are authenticated"""
        if not self.user.is_authenticated:
            return False
        try:
            User.objects.get(username=self.other_username)
            return True
        except User.DoesNotExist:
            return False

    def get_room_name(self):
        """Create consistent room name regardless of user order"""
        usernames = sorted([self.user.username, self.other_username])
        return f"{usernames[0]}_{usernames[1]}"

    @database_sync_to_async
    def save_message(self, content):
        """Save message to database"""
        receiver = User.objects.get(username=self.other_username)
        return Message.objects.create(
            sender=self.user,
            receiver=receiver,
            content=content
        )

    @database_sync_to_async
    def get_message_history(self):
        """Retrieve last 50 messages between users"""
        other_user = User.objects.get(username=self.other_username)
        messages = Message.objects.filter(
            Q(sender=self.user, receiver=other_user) |
            Q(sender=other_user, receiver=self.user)
        ).order_by('timestamp')[:50]

        return [{
            'content': msg.content,
            'sender': msg.sender.username,
            'timestamp': msg.timestamp.isoformat(),
            'message_id': msg.id,
            'read': msg.read
        } for msg in messages]

    @database_sync_to_async
    def mark_message_as_read(self, message_id):
        """Mark a message as read"""
        Message.objects.filter(
            id=message_id,
            receiver=self.user
        ).update(read=True)
