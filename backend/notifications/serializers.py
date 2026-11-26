from rest_framework import serializers
from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(source='uuid', read_only=True)

    class Meta:
        model = Notification
        fields = (
            'id',
            'uuid',
            'title',
            'message',
            'notification_type',
            'is_read',
            'created_at',
        )
        read_only_fields = ('id', 'uuid', 'title', 'message', 'notification_type', 'created_at')
