from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib.auth.models import User
from django.db.models import Q, Prefetch
from django.utils import timezone
import logging

from .models import Conversation, Message, MessageReadStatus
from .serializers import (
    ConversationSerializer, 
    ConversationDetailSerializer,
    MessageSerializer, 
    UserSerializer
)
from .permissions import IsParticipantOfConversation, IsMessageSender
from .filters import MessageFilter, ConversationFilter
from .pagination import MessagePagination, ConversationPagination

logger = logging.getLogger(__name__)

class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing conversations
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ConversationFilter
    search_fields = ['name', 'participants__username']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    pagination_class = ConversationPagination
    
    def get_queryset(self):
        """
        Return conversations where the current user is a participant
        """
        return Conversation.objects.filter(
            participants=self.request.user
        ).prefetch_related(
            'participants',
            Prefetch('messages', queryset=Message.objects.select_related('sender'))
        ).distinct()
    
    def get_serializer_class(self):
        """
        Return detailed serializer for retrieve action
        """
        if self.action == 'retrieve':
            return ConversationDetailSerializer
        return ConversationSerializer
    
    def perform_create(self, serializer):
        """
        Create a new conversation and add the current user as a participant
        """
        conversation = serializer.save()
        logger.info(f"User {self.request.user.username} created conversation {conversation.id}")
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        """
        Add a participant to the conversation
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            conversation.participants.add(user)
            logger.info(f"User {user.username} added to conversation {conversation.id}")
            return Response({'message': f'User {user.username} added to conversation'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        """
        Remove a participant from the conversation
        """
        conversation = self.get_object()
        user_id = request.data.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            if conversation.participants.count() <= 2:
                return Response(
                    {'error': 'Cannot remove participant from a conversation with only 2 participants'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            conversation.participants.remove(user)
            logger.info(f"User {user.username} removed from conversation {conversation.id}")
            return Response({'message': f'User {user.username} removed from conversation'})
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Mark all messages in the conversation as read for the current user
        """
        conversation = self.get_object()
        unread_messages = conversation.messages.exclude(
            read_statuses__user=request.user
        ).exclude(sender=request.user)
        
        for message in unread_messages:
            MessageReadStatus.objects.get_or_create(
                message=message,
                user=request.user
            )
        
        count = unread_messages.count()
        logger.info(f"User {request.user.username} marked {count} messages as read in conversation {conversation.id}")
        return Response({'message': f'Marked {count} messages as read'})

class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing messages
    """
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated, IsMessageSender]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = MessageFilter
    search_fields = ['content', 'sender__username']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    pagination_class = MessagePagination
    
    def get_queryset(self):
        """
        Return messages from conversations where the current user is a participant
        """
        user_conversations = Conversation.objects.filter(
            participants=self.request.user
        )
        return Message.objects.filter(
            conversation__in=user_conversations
        ).select_related('sender', 'conversation').prefetch_related(
            'read_statuses'
        )
    
    def perform_create(self, serializer):
        """
        Create a new message and update conversation timestamp
        """
        message = serializer.save(sender=self.request.user)
        # Update conversation's updated_at timestamp
        message.conversation.updated_at = timezone.now()
        message.conversation.save(update_fields=['updated_at'])
        logger.info(f"User {self.request.user.username} sent message in conversation {message.conversation.id}")
    
    def perform_update(self, serializer):
        """
        Update message and set edited timestamp
        """
        message = serializer.save(edited_at=timezone.now())
        logger.info(f"User {self.request.user.username} edited message {message.id}")
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Mark a specific message as read
        """
        message = self.get_object()
        read_status, created = MessageReadStatus.objects.get_or_create(
            message=message,
            user=request.user
        )
        
        if created:
            logger.info(f"User {request.user.username} marked message {message.id} as read")
            return Response({'message': 'Message marked as read'})
        else:
            return Response({'message': 'Message was already marked as read'})
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """
        Get all unread messages for the current user
        """
        unread_messages = self.get_queryset().exclude(
            read_statuses__user=request.user
        ).exclude(sender=request.user)
        
        page = self.paginate_queryset(unread_messages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(unread_messages, many=True)
        return Response(serializer.data)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing users (for finding conversation participants)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter]
    search_fields = ['username', 'first_name', 'last_name', 'email']
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user's information
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)