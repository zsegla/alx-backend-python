from django.contrib import admin
from .models import Conversation, Message, MessageReadStatus

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'is_group', 'created_at', 'updated_at']
    list_filter = ['is_group', 'created_at']
    search_fields = ['name', 'participants__username']
    filter_horizontal = ['participants']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'sender', 'conversation', 'timestamp', 'is_read']
    list_filter = ['is_read', 'timestamp', 'sender']
    search_fields = ['content', 'sender__username']
    readonly_fields = ['id', 'timestamp', 'edited_at']

@admin.register(MessageReadStatus)
class MessageReadStatusAdmin(admin.ModelAdmin):
    list_display = ['message', 'user', 'read_at']
    list_filter = ['read_at']
    search_fields = ['message__content', 'user__username']
