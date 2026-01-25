"""请假管理 API 视图"""
from rest_framework import generics, permissions, views
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q

from .base import LoggingMixin
from ...models import Employee, LeaveRequest, BusinessTrip, TravelExpense
from ...permissions import get_managed_department_ids, HasRBACPermission
from ...rbac import Permissions
from ...utils import log_event, api_success, api_error, get_client_ip
from ..serializers import (
    LeaveRequestSerializer, LeaveRequestWriteSerializer, LeaveApproveSerializer, 
    BusinessTripSerializer, BusinessTripWriteSerializer,
    TravelExpenseSerializer, TravelExpenseWriteSerializer
)


class LeaveListCreateAPIView(LoggingMixin, generics.ListCreateAPIView):
    """请假列表与创建"""
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    log_model_name = '请假'
    
    # RBAC 权限
    def get_rbac_permissions(self):
        if self.request.method == 'POST':
            return [Permissions.LEAVE_CREATE]
        return [Permissions.LEAVE_VIEW]
    
    def get_queryset(self):
        qs = LeaveRequest.objects.select_related(
            'employee',
            'employee__department',
            'employee__department__manager',
            'employee__department__manager__user'
        ).all().order_by('-created_at')
        
        user = self.request.user
        if not user.is_staff:
            # 部门经理可看本部门所有员工请假，普通员工只能看自己
            managed_dept_ids = get_managed_department_ids(user)
            if managed_dept_ids:
                qs = qs.filter(Q(employee__user=user) | Q(employee__department_id__in=managed_dept_ids))
            else:
                qs = qs.filter(employee__user=user)
        
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        
        leave_type_param = self.request.query_params.get('leave_type')
        if leave_type_param:
            qs = qs.filter(leave_type=leave_type_param)
        
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return LeaveRequestWriteSerializer
        return LeaveRequestSerializer
    
    def get_log_detail(self, obj):
        return f'{obj.employee.employee_id} {obj.start_date}~{obj.end_date}'

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        
        data = ser.validated_data
        if data.get('employee') is None:
            try:
                data['employee'] = Employee.objects.get(user=request.user)
            except Employee.DoesNotExist:
                return Response(api_error('当前账户未关联员工', code='no_employee'), status=400)
        
        # 限制重复离职申请
        if data.get('leave_type') == 'resignation':
            emp_obj = data['employee']
            if LeaveRequest.objects.filter(employee=emp_obj, leave_type='resignation', status='pending').exists():
                return Response(api_error('已有待审批的离职申请，不能重复提交', code='resignation_duplicate'), status=400)
        
        leave = ser.save()
        log_event(user=request.user, action='提交请假', detail=self.get_log_detail(leave), ip=get_client_ip(request))
        return Response(api_success(LeaveRequestSerializer(leave, context={'request': request}).data), status=201)


class LeaveApproveAPIView(views.APIView):
    """请假审批"""
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    rbac_perms = [Permissions.LEAVE_APPROVE]

    def _is_direct_manager(self, user, leave: LeaveRequest) -> bool:
        try:
            if not hasattr(user, 'employee') or not user.employee:
                return False
            dept = leave.employee.department if leave.employee else None
            return bool(dept and dept.manager and dept.manager.id == user.employee.id)
        except Exception:
            return False

    def _sync_overall_status(self, leave: LeaveRequest):
        if leave.resignation_manager_status == 'rejected' or leave.resignation_hr_status == 'rejected':
            leave.status = 'rejected'
        elif leave.resignation_manager_status == 'approved' and leave.resignation_hr_status == 'approved':
            leave.status = 'approved'
        else:
            leave.status = 'pending'

    def post(self, request, pk):
        leave = get_object_or_404(LeaveRequest, pk=pk)
        ser = LeaveApproveSerializer(data=request.data)
        if not ser.is_valid():
            return Response(api_error('参数错误', errors=ser.errors), status=400)
        
        action = ser.validated_data['action']
        comments = ser.validated_data.get('comments') or ''
        stage = ser.validated_data.get('stage')

        # 非离职申请审批
        if leave.leave_type != 'resignation':
            if not request.user.is_staff:
                return Response(api_error('仅人事可审批该类型的请假', code='forbidden'), status=403)
            leave.approved_by = request.user
            leave.approved_at = timezone.now()
            leave.status = 'approved' if action == 'approve' else 'rejected'
            leave.comments = comments
            leave.save()
            log_event(user=request.user, action='审批请假', detail=f'{leave.id} -> {leave.status}', ip=get_client_ip(request))
            return Response(api_success(LeaveRequestSerializer(leave, context={'request': request}).data))

        # 离职申请审批流程
        can_manager = self._is_direct_manager(request.user, leave) or request.user.is_staff
        is_hr = request.user.is_staff
        
        if not stage:
            stage = 'manager' if can_manager and leave.resignation_manager_status == 'pending' and not is_hr else 'hr'

        if stage == 'manager':
            if not can_manager:
                return Response(api_error('仅直属上级可执行该操作', code='forbidden'), status=403)
            if leave.resignation_manager_status != 'pending':
                return Response(api_error('直属上级已处理该申请', code='already_reviewed'), status=400)
            leave.resignation_manager_status = 'approved' if action == 'approve' else 'rejected'
            leave.resignation_manager_comment = comments
            leave.resignation_manager_by = request.user
            leave.resignation_manager_at = timezone.now()
            if action == 'reject':
                leave.comments = comments
                leave.approved_by = request.user
                leave.approved_at = timezone.now()
        
        elif stage == 'hr':
            if not is_hr:
                return Response(api_error('需要人事权限才能执行该操作', code='forbidden'), status=403)
            if leave.resignation_hr_status != 'pending':
                return Response(api_error('人事已处理该申请', code='already_reviewed'), status=400)
            if action == 'approve' and leave.resignation_manager_status != 'approved':
                return Response(api_error('请等待直属上级审批后再确认', code='manager_pending'), status=400)
            leave.resignation_hr_status = 'approved' if action == 'approve' else 'rejected'
            leave.resignation_hr_comment = comments
            leave.resignation_hr_by = request.user
            leave.resignation_hr_at = timezone.now()
            leave.approved_by = request.user
            leave.approved_at = timezone.now()
            leave.comments = comments
        else:
            return Response(api_error('未知审批阶段', code='invalid_stage'), status=400)

        self._sync_overall_status(leave)
        leave.save()
        log_event(user=request.user, action='审批离职申请', detail=f'{leave.id} stage={stage} -> {leave.status}', ip=get_client_ip(request))
        return Response(api_success(LeaveRequestSerializer(leave, context={'request': request}).data))


class LeaveCancelAPIView(views.APIView):
    """销假"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        leave = get_object_or_404(LeaveRequest, pk=pk)
        
        # 只能销假自己的请假记录
        if leave.employee.user != request.user and not request.user.is_staff:
            return Response(api_error('无权操作此记录', code='forbidden'), status=403)
        
        # 只有已批准的请假才能销假
        if leave.status != 'approved':
            return Response(api_error('只有已批准的请假才能销假', code='invalid_status'), status=400)
        
        # 更新状态为已销假
        leave.status = 'cancelled'
        leave.save()
        
        log_event(user=request.user, action='销假', detail=f'{leave.employee.employee_id} {leave.start_date}~{leave.end_date}', ip=get_client_ip(request))
        return Response(api_success({'message': '销假成功'}))


class LeaveUpdateAPIView(views.APIView):
    """变更请假申请"""
    permission_classes = [permissions.IsAuthenticated]
    
    def put(self, request, pk):
        leave = get_object_or_404(LeaveRequest, pk=pk)
        
        # 只能修改自己的请假记录
        if leave.employee.user != request.user and not request.user.is_staff:
            return Response(api_error('无权操作此记录', code='forbidden'), status=403)
        
        # 只有待审批的请假才能变更
        if leave.status != 'pending':
            return Response(api_error('只有待审批的请假才能变更', code='invalid_status'), status=400)
        
        # 更新字段
        if 'start_date' in request.data:
            leave.start_date = request.data['start_date']
        if 'end_date' in request.data:
            leave.end_date = request.data['end_date']
        if 'leave_type' in request.data:
            leave.leave_type = request.data['leave_type']
        if 'reason' in request.data:
            leave.reason = request.data['reason']
        
        leave.save()
        
        log_event(user=request.user, action='变更请假', detail=f'{leave.employee.employee_id} {leave.start_date}~{leave.end_date}', ip=get_client_ip(request))
        return Response(api_success(LeaveRequestSerializer(leave, context={'request': request}).data))


# ============ 出差管理 API ============

class BusinessTripListCreateAPIView(LoggingMixin, generics.ListCreateAPIView):
    """出差申请列表与创建"""
    serializer_class = BusinessTripSerializer
    permission_classes = [permissions.IsAuthenticated]
    log_model_name = '出差'
    
    def get_queryset(self):
        qs = BusinessTrip.objects.select_related(
            'employee',
            'employee__department',
        ).all().order_by('-created_at')
        
        user = self.request.user
        
        # 如果指定 my_only=true，只返回当前用户自己的出差记录
        my_only = self.request.query_params.get('my_only', '').lower() == 'true'
        
        if my_only or not user.is_staff:
            if my_only:
                # 强制只返回自己的
                qs = qs.filter(employee__user=user)
            else:
                # 部门经理可看本部门所有员工出差，普通员工只能看自己
                managed_dept_ids = get_managed_department_ids(user)
                if managed_dept_ids:
                    qs = qs.filter(Q(employee__user=user) | Q(employee__department_id__in=managed_dept_ids))
                else:
                    qs = qs.filter(employee__user=user)
        
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        
        trip_type_param = self.request.query_params.get('trip_type')
        if trip_type_param:
            qs = qs.filter(trip_type=trip_type_param)
        
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return BusinessTripWriteSerializer
        return BusinessTripSerializer
    
    def get_log_detail(self, obj):
        return f'{obj.employee.employee_id} {obj.destination} {obj.start_date}~{obj.end_date}'

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        
        data = ser.validated_data
        if data.get('employee') is None:
            try:
                data['employee'] = Employee.objects.get(user=request.user)
            except Employee.DoesNotExist:
                return Response(api_error('当前账户未关联员工', code='no_employee'), status=400)
        
        trip = ser.save()
        log_event(user=request.user, action='提交出差', detail=self.get_log_detail(trip), ip=get_client_ip(request))
        return Response(api_success(BusinessTripSerializer(trip, context={'request': request}).data), status=201)


class BusinessTripDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """出差申请详情/更新/删除"""
    queryset = BusinessTrip.objects.all()
    serializer_class = BusinessTripSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return BusinessTripWriteSerializer
        return BusinessTripSerializer
    
    def update(self, request, *args, **kwargs):
        trip = self.get_object()
        
        # 只能修改自己的出差记录
        if trip.employee.user != request.user and not request.user.is_staff:
            return Response(api_error('无权操作此记录', code='forbidden'), status=403)
        
        # 只有待审批的出差才能变更
        if trip.status != 'pending':
            return Response(api_error('只有待审批的出差才能变更', code='invalid_status'), status=400)
        
        # 更新字段
        if 'destination' in request.data:
            trip.destination = request.data['destination']
        if 'trip_type' in request.data:
            trip.trip_type = request.data['trip_type']
        if 'start_date' in request.data:
            trip.start_date = request.data['start_date']
        if 'end_date' in request.data:
            trip.end_date = request.data['end_date']
        if 'days' in request.data:
            trip.days = request.data['days']
        if 'reason' in request.data:
            trip.reason = request.data['reason']
        if 'remarks' in request.data:
            trip.remarks = request.data['remarks']
        
        trip.save()
        
        log_event(user=request.user, action='变更出差', detail=f'{trip.employee.employee_id} {trip.destination}', ip=get_client_ip(request))
        return Response(api_success(BusinessTripSerializer(trip, context={'request': request}).data))


class BusinessTripApproveAPIView(views.APIView):
    """出差审批"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        trip = get_object_or_404(BusinessTrip, pk=pk)
        
        action = request.data.get('action')
        comments = request.data.get('comments', '')
        
        if action not in ['approve', 'reject']:
            return Response(api_error('无效的操作', code='invalid_action'), status=400)
        
        if not request.user.is_staff:
            return Response(api_error('仅人事可审批出差', code='forbidden'), status=403)
        
        if trip.status != 'pending':
            return Response(api_error('该申请已处理', code='already_processed'), status=400)
        
        trip.approved_by = request.user
        trip.approved_at = timezone.now()
        trip.status = 'approved' if action == 'approve' else 'rejected'
        trip.comments = comments
        trip.save()
        
        log_event(user=request.user, action='审批出差', detail=f'{trip.id} -> {trip.status}', ip=get_client_ip(request))
        return Response(api_success(BusinessTripSerializer(trip, context={'request': request}).data))


class BusinessTripCancelAPIView(views.APIView):
    """取消出差"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk):
        trip = get_object_or_404(BusinessTrip, pk=pk)
        
        # 只能取消自己的出差记录
        if trip.employee.user != request.user and not request.user.is_staff:
            return Response(api_error('无权操作此记录', code='forbidden'), status=403)
        
        # 只有已批准的出差才能取消
        if trip.status != 'approved':
            return Response(api_error('只有已批准的出差才能取消', code='invalid_status'), status=400)
        
        # 更新状态为已取消
        trip.status = 'cancelled'
        trip.save()
        
        log_event(user=request.user, action='取消出差', detail=f'{trip.employee.employee_id} {trip.destination}', ip=get_client_ip(request))
        return Response(api_success({'message': '取消成功'}))


class TravelExpenseListCreateAPIView(LoggingMixin, generics.ListCreateAPIView):
    """差旅报销列表与创建"""
    serializer_class = TravelExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    log_model_name = '差旅报销'
    
    def get_queryset(self):
        qs = TravelExpense.objects.select_related(
            'employee', 'employee__department', 'business_trip', 'approved_by'
        ).all().order_by('-created_at')
        
        user = self.request.user
        if not user.is_staff:
            # 普通员工只能看自己的报销记录
            try:
                emp = user.employee
                qs = qs.filter(employee=emp)
            except Employee.DoesNotExist:
                qs = qs.none()
        
        # 筛选参数
        status = self.request.query_params.get('status')
        expense_type = self.request.query_params.get('expense_type')
        
        if status:
            qs = qs.filter(status=status)
        if expense_type:
            qs = qs.filter(expense_type=expense_type)
        
        return qs
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return TravelExpenseWriteSerializer
        return TravelExpenseSerializer
    
    def perform_create(self, serializer):
        try:
            emp = self.request.user.employee
        except Employee.DoesNotExist:
            raise Exception('当前用户无关联员工')
        serializer.save(employee=emp)
        log_event(
            user=self.request.user,
            action='申请差旅报销',
            detail=f'{emp.employee_id} ¥{serializer.validated_data.get("amount")}',
            ip=get_client_ip(self.request)
        )


class TravelExpenseDetailAPIView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """差旅报销详情"""
    serializer_class = TravelExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    log_model_name = '差旅报销'
    
    def get_queryset(self):
        user = self.request.user
        qs = TravelExpense.objects.select_related('employee', 'business_trip', 'approved_by')
        if not user.is_staff:
            try:
                emp = user.employee
                qs = qs.filter(employee=emp)
            except Employee.DoesNotExist:
                qs = qs.none()
        return qs
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return TravelExpenseWriteSerializer
        return TravelExpenseSerializer
    
    def update(self, request, *args, **kwargs):
        expense = self.get_object()
        
        # 只有待审批状态才能修改
        if expense.status != 'pending':
            return Response(api_error('只有待审批的报销才能修改', code='invalid_status'), status=400)
        
        return super().update(request, *args, **kwargs)


class TravelExpenseApproveAPIView(views.APIView):
    """差旅报销审批"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        expense = get_object_or_404(TravelExpense, pk=pk)
        
        action = request.data.get('action')
        comments = request.data.get('comments', '')
        
        if action not in ['approve', 'reject']:
            return Response(api_error('无效的操作', code='invalid_action'), status=400)
        
        if not request.user.is_staff:
            return Response(api_error('仅人事可审批报销', code='forbidden'), status=403)
        
        if expense.status != 'pending':
            return Response(api_error('该申请已处理', code='already_processed'), status=400)
        
        expense.approved_by = request.user
        expense.approved_at = timezone.now()
        expense.status = 'approved' if action == 'approve' else 'rejected'
        expense.comments = comments
        expense.save()
        
        log_event(user=request.user, action='审批差旅报销', detail=f'{expense.id} -> {expense.status}', ip=get_client_ip(request))
        return Response(api_success(TravelExpenseSerializer(expense, context={'request': request}).data))


class TravelExpensePayAPIView(views.APIView):
    """差旅报销发放"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        expense = get_object_or_404(TravelExpense, pk=pk)
        
        if not request.user.is_staff:
            return Response(api_error('仅人事可执行报销发放', code='forbidden'), status=403)
        
        if expense.status != 'approved':
            return Response(api_error('只有已批准的报销才能发放', code='invalid_status'), status=400)
        
        expense.status = 'paid'
        expense.paid_at = timezone.now()
        expense.save()
        
        log_event(user=request.user, action='发放差旅报销', detail=f'{expense.id} ¥{expense.amount}', ip=get_client_ip(request))
        return Response(api_success(TravelExpenseSerializer(expense, context={'request': request}).data))
