

from rest_framework import serializers
from .models import Message, ContactInfo

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'timestamp', 'contact']

class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = ['id', 'token_number', 'contact_type', 'contact_value', 'ip_address',
                  'mobile', 'email', 'created_at', 'is_seen']
