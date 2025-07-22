from django.db import models
from django.contrib.auth.models import User


class ChatRoom(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms2')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user1', 'user2')  # Ensures only one chat room per pair
        ordering = ['-created_at']

    def __str__(self):
        return f"Chat between {self.user1} and {self.user2}"


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.sender} at {self.timestamp}: {self.content[:30]}"
