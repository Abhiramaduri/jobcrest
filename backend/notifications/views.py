from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework import status

from accounts.lookup import get_object_by_uuid_or_id
from .models import Notification
from .serializers import NotificationSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list_view(request):
    """Lists notifications for the authenticated user (most recent first), with optional is_read filtering."""
    queryset = Notification.objects.filter(user=request.user).order_by('-created_at')

    is_read_param = request.query_params.get('is_read')
    if is_read_param is not None:
        normalized = is_read_param.strip().lower()
        if normalized in ('true', '1', 'yes'):
            queryset = queryset.filter(is_read=True)
        elif normalized in ('false', '0', 'no'):
            queryset = queryset.filter(is_read=False)

    paginator_class = api_settings.DEFAULT_PAGINATION_CLASS
    if paginator_class is not None:
        paginator = paginator_class()
        page = paginator.paginate_queryset(queryset, request)
        if page is not None:
            serializer = NotificationSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

    return Response(NotificationSerializer(queryset, many=True).data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_unread_count_view(request):
    """Returns the count of unread notifications for the authenticated user."""
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return Response({'unread_count': unread_count}, status=status.HTTP_200_OK)


@api_view(['PATCH', 'POST'])
@permission_classes([IsAuthenticated])
def notification_mark_read_view(request, pk):
    """Marks a single notification owned by the authenticated user as read."""
    notification = get_object_by_uuid_or_id(
        Notification.objects.filter(user=request.user),
        pk,
    )
    if not notification.is_read:
        notification.is_read = True
        notification.save(update_fields=['is_read'])
    return Response(NotificationSerializer(notification).data, status=status.HTTP_200_OK)


@api_view(['POST', 'PATCH'])
@permission_classes([IsAuthenticated])
def notification_mark_all_read_view(request):
    """Marks all unread notifications owned by the authenticated user as read."""
    updated_count = Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return Response(
        {'updated': updated_count, 'unread_count': 0},
        status=status.HTTP_200_OK,
    )
