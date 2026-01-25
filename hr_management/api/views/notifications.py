"""
通知 API 视图
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from ...notifications import NotificationManager


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_list(request):
    """获取用户通知列表"""
    unread_only = request.query_params.get('unread_only', 'false').lower() == 'true'
    limit = int(request.query_params.get('limit', 20))
    
    notifications = NotificationManager.get_notifications(
        user_id=request.user.id,
        unread_only=unread_only,
        limit=limit
    )
    
    unread_count = NotificationManager.get_unread_count(request.user.id)
    
    return Response({
        'notifications': notifications,
        'unread_count': unread_count,
        'total': len(notifications),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def notification_unread_count(request):
    """获取未读通知数量"""
    count = NotificationManager.get_unread_count(request.user.id)
    return Response({'unread_count': count})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def notification_mark_read(request, notification_id):
    """标记单个通知为已读"""
    success = NotificationManager.mark_as_read(
        user_id=request.user.id,
        notification_id=notification_id
    )
    
    if success:
        return Response({'message': '已标记为已读'})
    return Response(
        {'detail': '通知不存在'},
        status=status.HTTP_404_NOT_FOUND
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def notification_mark_all_read(request):
    """标记所有通知为已读"""
    count = NotificationManager.mark_all_as_read(request.user.id)
    return Response({
        'message': f'已将 {count} 条通知标记为已读',
        'count': count
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def notification_clear(request):
    """清除所有通知"""
    count = NotificationManager.clear_notifications(request.user.id)
    return Response({
        'message': f'已清除 {count} 条通知',
        'count': count
    })
