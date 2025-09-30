

# from rest_framework import serializers
# from .models import Message, ContactInfo

# class MessageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Message
#         fields = ['id', 'sender', 'text', 'timestamp', 'contact']

# class ContactInfoSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ContactInfo
#         fields = ['id', 'token_number', 'contact_type', 'contact_value', 'ip_address',
#                   'mobile', 'email', 'created_at', 'is_seen']




from rest_framework import serializers
from .models import Message, ContactInfo, WebsiteRegistration
# ----------------- Messages -----------------
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'text', 'timestamp', 'chat']

# ----------------- Contact Info -----------------
class ContactInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactInfo
        fields = ['id', 'token_number', 'contact_type', 'contact_value', 
                  'ip_address', 'mobile', 'email', 'created_at', 'is_seen']

# ----------------- Website Registration -----------------
class WebsiteRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WebsiteRegistration
        fields = '__all__'

