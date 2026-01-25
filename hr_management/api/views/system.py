"""系统管理 API 视图（日志、备份、文档）"""
import shutil
from pathlib import Path

from django.conf import settings
from django.db import connections
from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .base import LoggingMixin
from ...models import SystemLog, CompanyDocument, RBACPermission
from ...permissions import IsStaffOrOwner, HasRBACPermission, user_has_rbac_permission
from ...rbac import Permissions
from ...utils import api_error, api_success, log_event
from ..serializers import (
    SystemLogSerializer, 
    CompanyDocumentSerializer, CompanyDocumentWriteSerializer
)


# ==================== 系统日志 ====================

class SystemLogListAPIView(generics.ListAPIView):
    """系统日志列表"""
    serializer_class = SystemLogSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.SYSTEM_LOG_VIEW]
    
    def get_queryset(self):
        qs = SystemLog.objects.select_related('user').all().order_by('-timestamp')
        level = self.request.query_params.get('level')
        if level:
            qs = qs.filter(level=level)
        return qs[:500]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def system_log_clear(request):
    """清空系统日志"""
    # 权限检查
    if not (request.user.is_superuser or user_has_rbac_permission(request.user, Permissions.SYSTEM_LOG_CLEAR)):
        return Response(api_error('无清除日志权限', code='forbidden'), status=403)
    
    level = request.data.get('level')
    qs = SystemLog.objects.all()
    if level:
        qs = qs.filter(level=level)
    count = qs.count()
    qs.delete()
    log_event(
        user=request.user, 
        action='清空系统日志', 
        level='WARNING', 
        detail=f'{count} rows (level={level or "*"})', 
        ip=request.META.get('REMOTE_ADDR')
    )
    return Response(api_success(detail=f'已删除 {count} 条日志'))


# ==================== 备份管理 ====================

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def backups_list(request):
    """获取备份列表"""
    # 权限检查
    if not (request.user.is_superuser or user_has_rbac_permission(request.user, Permissions.SYSTEM_BACKUP_VIEW)):
        return Response(api_error('无查看备份权限', code='forbidden'), status=403)
    
    backup_dir = Path(settings.MEDIA_ROOT) / 'backups'
    backup_dir.mkdir(parents=True, exist_ok=True)
    items = []
    for f in sorted(backup_dir.glob('backup_*.sqlite3'), key=lambda p: p.stat().st_mtime, reverse=True):
        st = f.stat()
        items.append({
            'name': f.name,
            'size': st.st_size,
            'mtime': st.st_mtime,
        })
    return Response({'backups': items})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def backup_create(request):
    """创建备份"""
    # 权限检查
    if not (request.user.is_superuser or user_has_rbac_permission(request.user, Permissions.SYSTEM_BACKUP_CREATE)):
        return Response(api_error('无创建备份权限', code='forbidden'), status=403)
    
    db_path = Path(settings.DATABASES['default']['NAME'])
    if not db_path.exists():
        return Response({'detail': '数据库文件不存在'}, status=400)
    
    backup_dir = Path(settings.MEDIA_ROOT) / 'backups'
    backup_dir.mkdir(parents=True, exist_ok=True)
    ts = timezone.now().strftime('%Y%m%d_%H%M%S')
    target = backup_dir / f'backup_{ts}.sqlite3'
    
    connections.close_all()
    shutil.copy2(db_path, target)
    log_event(
        user=request.user, 
        action='创建备份', 
        level='INFO', 
        detail=target.name, 
        ip=request.META.get('REMOTE_ADDR')
    )
    return Response({'detail': '备份创建成功', 'file': target.name})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def backup_clean(request):
    """清理旧备份"""
    # 权限检查
    if not (request.user.is_superuser or user_has_rbac_permission(request.user, Permissions.SYSTEM_BACKUP_CREATE)):
        return Response(api_error('无管理备份权限', code='forbidden'), status=403)
    
    keep = int(request.data.get('keep', 5))
    if keep < 1:
        keep = 1
    
    backup_dir = Path(settings.MEDIA_ROOT) / 'backups'
    files = sorted(backup_dir.glob('backup_*.sqlite3'), key=lambda p: p.stat().st_mtime, reverse=True)
    removed = []
    for f in files[keep:]:
        try:
            f.unlink()
            removed.append(f.name)
        except Exception:
            pass
    
    if removed:
        log_event(
            user=request.user, 
            action='清理备份', 
            level='INFO', 
            detail='删除: ' + ', '.join(removed), 
            ip=request.META.get('REMOTE_ADDR')
        )
    return Response({'detail': '清理完成', 'removed': removed, 'kept': keep})


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def backup_restore(request):
    """从备份恢复数据库"""
    # 权限检查
    if not (request.user.is_superuser or user_has_rbac_permission(request.user, Permissions.SYSTEM_BACKUP_RESTORE)):
        return Response(api_error('无恢复备份权限', code='forbidden'), status=403)
    
    filename = request.data.get('filename')
    if not filename:
        return Response({'detail': '缺少 filename'}, status=400)
    
    backup_dir = Path(settings.MEDIA_ROOT) / 'backups'
    target = (backup_dir / filename).resolve()
    if backup_dir not in target.parents or not target.exists() or not target.name.startswith('backup_'):
        return Response({'detail': '非法备份文件'}, status=400)
    
    db_path = Path(settings.DATABASES['default']['NAME']).resolve()
    try:
        connections.close_all()
        auto_backup = backup_dir / f"auto_before_restore_{timezone.now().strftime('%Y%m%d_%H%M%S')}.sqlite3"
        if db_path.exists():
            shutil.copy2(db_path, auto_backup)
        shutil.copy2(target, db_path)
        log_event(
            user=request.user, 
            action='恢复备份', 
            level='WARNING', 
            detail=f'从 {target.name} 恢复', 
            ip=request.META.get('REMOTE_ADDR')
        )
        return Response({'detail': '恢复成功', 'from': target.name, 'auto_backup': auto_backup.name})
    except Exception as e:
        return Response({'detail': f'恢复失败: {e}'}, status=500)


# ==================== 公司文档 ====================

class CompanyDocumentListCreateAPIView(LoggingMixin, generics.ListCreateAPIView):
    """公司文档列表与创建"""
    serializer_class = CompanyDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    queryset = CompanyDocument.objects.select_related('uploaded_by').all().order_by('-created_at')
    log_model_name = '文档'
    
    # RBAC 权限
    def get_rbac_permissions(self):
        if self.request.method == 'POST':
            return [Permissions.DOCUMENT_CREATE]
        return [Permissions.DOCUMENT_VIEW]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CompanyDocumentWriteSerializer
        return CompanyDocumentSerializer
    
    def get_log_detail(self, obj):
        return obj.title

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        doc = ser.save(uploaded_by=request.user)
        self.log_create(request, doc)
        return Response(api_success(CompanyDocumentSerializer(doc, context={'request': request}).data), status=201)


class CompanyDocumentDetailAPIView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """公司文档详情、更新、删除"""
    queryset = CompanyDocument.objects.select_related('uploaded_by').all()
    serializer_class = CompanyDocumentSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    log_model_name = '文档'
    
    # RBAC 权限
    def get_rbac_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [Permissions.DOCUMENT_EDIT]
        if self.request.method == 'DELETE':
            return [Permissions.DOCUMENT_DELETE]
        return [Permissions.DOCUMENT_VIEW]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CompanyDocumentWriteSerializer
        return CompanyDocumentSerializer
    
    def get_log_detail(self, obj):
        return f'{obj.title} v{obj.version}'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        ser = self.get_serializer(instance, data=request.data, partial=(request.method == 'PATCH'))
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        doc = ser.save()
        self.log_update(request, doc)
        return Response(api_success(CompanyDocumentSerializer(doc, context={'request': request}).data))

    def destroy(self, request, *args, **kwargs):
        doc = self.get_object()
        self.log_delete(request, doc)
        title = doc.title
        doc.delete()
        return Response(api_success(detail=f'已删除 {title}'))


# ==================== 系统监控 ====================

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """
    系统健康检查端点
    - 无需认证，用于负载均衡器和监控系统
    - 返回基本健康状态
    """
    from ...monitoring import check_database_health
    
    db_health = check_database_health()
    
    if db_health['status'] == 'healthy':
        return Response({
            'status': 'ok',
            'database': 'connected'
        })
    else:
        return Response({
            'status': 'error',
            'database': 'disconnected',
            'error': db_health.get('error')
        }, status=503)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def health_report(request):
    """
    详细健康报告
    - 需要认证
    - 返回完整的系统指标
    """
    # 权限检查：仅管理员或有系统监控权限的用户
    if not (request.user.is_superuser or request.user.is_staff):
        return Response(api_error('无查看系统监控权限', code='forbidden'), status=403)
    
    from ...monitoring import get_health_report
    
    report = get_health_report()
    return Response(api_success(report))


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def system_metrics(request):
    """
    系统指标端点
    - 返回 CPU、内存、磁盘等指标
    """
    if not (request.user.is_superuser or request.user.is_staff):
        return Response(api_error('无查看系统监控权限', code='forbidden'), status=403)
    
    from ...monitoring import metrics
    
    return Response(api_success(metrics.get_metrics()))

