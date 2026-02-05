"""薪资管理 API 视图"""
from rest_framework import generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone

from .base import LoggingMixin
from ...models import SalaryRecord, SystemLog
from ...permissions import IsStaffOrOwnRelated, get_managed_department_ids, HasRBACPermission, user_has_rbac_permission
from ...rbac import Permissions
from ...utils import api_success, api_error
from ...notifications import notify_salary_issued
from ..serializers import SalaryRecordSerializer, SalaryRecordWriteSerializer


class SalaryListCreateAPIView(LoggingMixin, generics.ListCreateAPIView):
    """薪资列表与创建"""
    serializer_class = SalaryRecordSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    log_model_name = '薪资记录'

    # RBAC 权限
    def get_rbac_permissions(self):
        if self.request.method == 'POST':
            return [Permissions.SALARY_CREATE]
        return [Permissions.SALARY_VIEW]

    def get_queryset(self):
        qs = SalaryRecord.objects.select_related('employee', 'employee__department').all().order_by('-year', '-month')
        user = self.request.user
        if not user.is_staff:
            # 部门经理可看本部门所有员工薪资，普通员工只能看自己
            managed_dept_ids = get_managed_department_ids(user)
            if managed_dept_ids:
                qs = qs.filter(Q(employee__user=user) | Q(employee__department_id__in=managed_dept_ids))
            else:
                qs = qs.filter(employee__user=user)

        # 按员工ID筛选
        employee_id = self.request.query_params.get('employee')
        if employee_id:
            qs = qs.filter(employee_id=employee_id)

        year = self.request.query_params.get('year')
        if year:
            qs = qs.filter(year=year)

        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return SalaryRecordWriteSerializer
        return SalaryRecordSerializer

    def get_log_detail(self, obj):
        return f'{obj.employee.employee_id} {obj.year}-{obj.month}'

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        salary = ser.save()
        self.log_create(request, salary)
        return Response(api_success(SalaryRecordSerializer(salary).data), status=201)


class SalaryDetailAPIView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """薪资详情、更新、删除"""
    queryset = SalaryRecord.objects.select_related('employee').all()
    serializer_class = SalaryRecordSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    log_model_name = '薪资记录'

    # RBAC 权限
    def get_rbac_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [Permissions.SALARY_EDIT]
        if self.request.method == 'DELETE':
            return [Permissions.SALARY_EDIT]
        return [Permissions.SALARY_VIEW]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return SalaryRecordWriteSerializer
        return SalaryRecordSerializer

    def get_log_detail(self, obj):
        return f'{obj.employee.employee_id} {obj.year}-{obj.month}'

    def update(self, request, *args, **kwargs):
        partial = request.method == 'PATCH'
        instance = self.get_object()
        ser = self.get_serializer(instance, data=request.data, partial=partial)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        record = ser.save()
        self.log_update(request, record)
        return Response(api_success(SalaryRecordSerializer(record).data))

    def destroy(self, request, *args, **kwargs):
        record = self.get_object()
        self.log_delete(request, record)
        detail = self.get_log_detail(record)
        record.delete()
        return Response(api_success(detail=f'已删除 {detail}'))


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def salary_disburse(request):
    """
    批量发放薪资
    POST /api/salaries/disburse/
    Body: { "year": 2026, "month": 1 } 或 { "ids": [1, 2, 3] }
    """
    # 权限检查
    if not (request.user.is_staff or request.user.is_superuser or
            user_has_rbac_permission(request.user, Permissions.SALARY_DISBURSE)):
        return Response(api_error('无发放薪资权限'), status=403)

    ids = request.data.get('ids')
    year = request.data.get('year')
    month = request.data.get('month')

    if ids:
        # 按ID列表发放
        records = SalaryRecord.objects.filter(id__in=ids, paid=False)
    elif year and month:
        # 按年月发放
        records = SalaryRecord.objects.filter(year=year, month=month, paid=False)
    else:
        return Response(api_error('请提供 ids 或 year+month 参数'), status=400)

    if not records.exists():
        return Response(api_error('没有待发放的薪资记录'), status=400)

    # 先保存要更新的ID列表
    record_ids = list(records.values_list('id', flat=True))
    count = len(record_ids)
    now = timezone.now()

    # 批量更新
    records.update(paid=True, paid_at=now)

    # 发送通知给每位员工
    for record in SalaryRecord.objects.filter(id__in=record_ids).select_related('employee'):
        if record.employee and record.employee.user:
            try:
                notify_salary_issued(
                    record.employee.user,
                    f'{record.year}年{record.month}月',
                    float(record.net_salary)
                )
            except Exception:
                pass  # 通知失败不影响发放

    # 记录日志
    SystemLog.objects.create(
        user=request.user,
        action='发放薪资',
        detail=f'批量发放 {count} 条薪资记录 (year={year}, month={month}, ids={record_ids[:10]}...)'
    )

    return Response(api_success({
        'count': count,
        'paid_at': now.isoformat()
    }, detail=f'成功发放 {count} 条薪资记录'))


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def salary_pending(request):
    """
    获取待发放薪资汇总
    GET /api/salaries/pending/
    """
    if not (request.user.is_staff or request.user.is_superuser or
            user_has_rbac_permission(request.user, Permissions.SALARY_VIEW)):
        return Response(api_error('无查看薪资权限'), status=403)

    # 获取所有未发放的记录，按年月分组
    from django.db.models import Sum, Count
    pending = SalaryRecord.objects.filter(paid=False).values('year', 'month').annotate(
        count=Count('id'),
        total=Sum('net_salary')
    ).order_by('-year', '-month')

    return Response(api_success(list(pending)))

