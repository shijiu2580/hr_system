"""
WebSocket 实时通知模块
提供审批通知、系统消息等实时推送功能

注意：需要安装 channels 和 channels-redis
pip install channels channels-redis

在 settings.py 中添加：
INSTALLED_APPS += ['channels']
ASGI_APPLICATION = 'hr_system.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
        # 生产环境使用 Redis:
        # 'BACKEND': 'channels_redis.core.RedisChannelLayer',
        # 'CONFIG': {'hosts': [('127.0.0.1', 6379)]},
    },
}
"""
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum


class NotificationType(str, Enum):
    """通知类型"""
    # 审批相关
    LEAVE_PENDING = 'leave_pending'           # 请假待审批
    LEAVE_APPROVED = 'leave_approved'         # 请假已批准
    LEAVE_REJECTED = 'leave_rejected'         # 请假已拒绝
    
    TRIP_PENDING = 'trip_pending'             # 出差待审批
    TRIP_APPROVED = 'trip_approved'           # 出差已批准
    TRIP_REJECTED = 'trip_rejected'           # 出差已拒绝
    
    EXPENSE_PENDING = 'expense_pending'       # 报销待审批
    EXPENSE_APPROVED = 'expense_approved'     # 报销已批准
    EXPENSE_REJECTED = 'expense_rejected'     # 报销已拒绝
    EXPENSE_PAID = 'expense_paid'             # 报销已支付
    
    ATTENDANCE_SUPPLEMENT = 'attendance_supplement'  # 补卡待审批
    
    # 系统相关
    SYSTEM_ANNOUNCEMENT = 'system_announcement'  # 系统公告
    SALARY_ISSUED = 'salary_issued'              # 工资已发放
    CONTRACT_EXPIRING = 'contract_expiring'      # 合同即将到期
    
    # 消息相关
    NEW_MESSAGE = 'new_message'               # 新消息
    MENTION = 'mention'                       # @提醒


@dataclass
class Notification:
    """通知数据结构"""
    id: str
    type: NotificationType
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    read: bool = False
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'type': self.type.value if isinstance(self.type, NotificationType) else self.type,
            'title': self.title,
            'message': self.message,
            'data': self.data,
            'read': self.read,
            'created_at': self.created_at,
        }


class NotificationManager:
    """
    通知管理器 - 简化版（不依赖 channels）
    使用轮询模式，可以升级到 WebSocket
    """
    
    # 内存存储通知（生产环境应使用 Redis）
    _notifications: Dict[int, List[Notification]] = {}
    _max_notifications = 100  # 每用户最大通知数
    
    @classmethod
    def add_notification(
        cls, 
        user_id: int, 
        notification_type: NotificationType,
        title: str,
        message: str,
        data: dict = None
    ) -> Notification:
        """添加通知"""
        import uuid
        
        notification = Notification(
            id=str(uuid.uuid4()),
            type=notification_type,
            title=title,
            message=message,
            data=data,
        )
        
        if user_id not in cls._notifications:
            cls._notifications[user_id] = []
        
        cls._notifications[user_id].insert(0, notification)
        
        # 限制通知数量
        if len(cls._notifications[user_id]) > cls._max_notifications:
            cls._notifications[user_id] = cls._notifications[user_id][:cls._max_notifications]
        
        return notification
    
    @classmethod
    def get_notifications(
        cls, 
        user_id: int, 
        unread_only: bool = False,
        limit: int = 20
    ) -> List[dict]:
        """获取用户通知"""
        notifications = cls._notifications.get(user_id, [])
        
        if unread_only:
            notifications = [n for n in notifications if not n.read]
        
        return [n.to_dict() for n in notifications[:limit]]
    
    @classmethod
    def get_unread_count(cls, user_id: int) -> int:
        """获取未读通知数量"""
        notifications = cls._notifications.get(user_id, [])
        return sum(1 for n in notifications if not n.read)
    
    @classmethod
    def mark_as_read(cls, user_id: int, notification_id: str) -> bool:
        """标记通知为已读"""
        notifications = cls._notifications.get(user_id, [])
        for notification in notifications:
            if notification.id == notification_id:
                notification.read = True
                return True
        return False
    
    @classmethod
    def mark_all_as_read(cls, user_id: int) -> int:
        """标记所有通知为已读"""
        notifications = cls._notifications.get(user_id, [])
        count = 0
        for notification in notifications:
            if not notification.read:
                notification.read = True
                count += 1
        return count
    
    @classmethod
    def clear_notifications(cls, user_id: int) -> int:
        """清除用户所有通知"""
        count = len(cls._notifications.get(user_id, []))
        cls._notifications[user_id] = []
        return count


# 便捷通知函数
def notify_leave_pending(approver_id: int, employee_name: str, leave_type: str, leave_id: int):
    """通知审批人有新的请假待审批"""
    return NotificationManager.add_notification(
        user_id=approver_id,
        notification_type=NotificationType.LEAVE_PENDING,
        title='新的请假申请',
        message=f'{employee_name} 提交了 {leave_type} 申请，请及时审批',
        data={'leave_id': leave_id, 'employee_name': employee_name}
    )


def notify_leave_result(employee_user_id: int, approved: bool, leave_type: str, reason: str = None):
    """通知员工请假审批结果"""
    notification_type = NotificationType.LEAVE_APPROVED if approved else NotificationType.LEAVE_REJECTED
    title = '请假已批准' if approved else '请假被拒绝'
    message = f'您的 {leave_type} 申请已{"批准" if approved else "被拒绝"}'
    if reason:
        message += f'，原因：{reason}'
    
    return NotificationManager.add_notification(
        user_id=employee_user_id,
        notification_type=notification_type,
        title=title,
        message=message,
    )


def notify_expense_result(employee_user_id: int, status: str, amount: float, expense_id: int):
    """通知员工报销结果"""
    status_map = {
        'approved': (NotificationType.EXPENSE_APPROVED, '报销已批准', '您的报销申请已批准'),
        'rejected': (NotificationType.EXPENSE_REJECTED, '报销被拒绝', '您的报销申请被拒绝'),
        'paid': (NotificationType.EXPENSE_PAID, '报销已支付', f'您的报销 ¥{amount:.2f} 已支付'),
    }
    
    notification_type, title, message = status_map.get(
        status, 
        (NotificationType.EXPENSE_PENDING, '报销状态更新', '您的报销申请状态已更新')
    )
    
    return NotificationManager.add_notification(
        user_id=employee_user_id,
        notification_type=notification_type,
        title=title,
        message=message,
        data={'expense_id': expense_id, 'amount': amount}
    )


def notify_salary_issued(employee_user_id: int, month: str, net_salary: float):
    """通知员工工资已发放"""
    return NotificationManager.add_notification(
        user_id=employee_user_id,
        notification_type=NotificationType.SALARY_ISSUED,
        title='工资已发放',
        message=f'{month} 工资 ¥{net_salary:.2f} 已发放，请查收',
        data={'month': month, 'amount': net_salary}
    )


def notify_contract_expiring(employee_user_id: int, days_remaining: int):
    """通知员工合同即将到期"""
    return NotificationManager.add_notification(
        user_id=employee_user_id,
        notification_type=NotificationType.CONTRACT_EXPIRING,
        title='合同即将到期',
        message=f'您的劳动合同将在 {days_remaining} 天后到期，请联系人事部门',
        data={'days_remaining': days_remaining}
    )


def notify_system_announcement(user_ids: List[int], title: str, content: str):
    """发送系统公告"""
    notifications = []
    for user_id in user_ids:
        notification = NotificationManager.add_notification(
            user_id=user_id,
            notification_type=NotificationType.SYSTEM_ANNOUNCEMENT,
            title=title,
            message=content,
        )
        notifications.append(notification)
    return notifications
