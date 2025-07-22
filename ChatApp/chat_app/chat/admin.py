from django.contrib import admin
from .models import ChatRoom, Message

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('id', 'user1', 'user2', 'created_at')
    search_fields = ('user1__username', 'user2__username')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'content', 'timestamp', 'read')
    search_fields = ('sender__username', 'receiver__username', 'content')
    list_filter = ('read', 'timestamp')
