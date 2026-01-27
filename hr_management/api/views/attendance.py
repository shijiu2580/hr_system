"""考勤管理 API 视图"""
import math
from rest_framework import generics, permissions, views
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils import timezone
from django.db.models import Q

from .base import LoggingMixin
from ...models import Employee, Attendance, AttendanceSupplement, CheckInLocation
from ...permissions import IsStaffOrOwnRelated, get_managed_department_ids, HasRBACPermission
from ...rbac import Permissions
from ...utils import log_event, api_success, api_error, get_client_ip
from ..serializers import AttendanceSerializer, AttendanceWriteSerializer, CheckInLocationSerializer, CheckInLocationWriteSerializer


def calculate_distance(lat1, lng1, lat2, lng2):
    """使用 Haversine 公式计算两点间距离（米）"""
    R = 6371000  # 地球半径（米）

    lat1_rad = math.radians(float(lat1))
    lat2_rad = math.radians(float(lat2))
    delta_lat = math.radians(float(lat2) - float(lat1))
    delta_lng = math.radians(float(lng2) - float(lng1))

    a = math.sin(delta_lat / 2) ** 2 + \
        math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


def check_location_in_range(latitude, longitude, employee=None):
    """
    检查给定位置是否在签到地点范围内
    如果员工关联了考勤地点，则只检查关联的地点
    否则检查所有启用的签到地点
    返回: (是否在范围内, 最近的签到点, 距离)
    """
    # 判断使用哪些签到地点
    if employee and employee.checkin_locations.exists():
        # 员工有关联的考勤地点，只检查关联的且启用的地点
        active_locations = employee.checkin_locations.filter(is_active=True)
    else:
        # 没有关联，使用所有启用的签到地点
        active_locations = CheckInLocation.objects.filter(is_active=True)

    if not active_locations.exists():
        # 没有设置签到地点，允许任何位置签到
        return True, None, 0

    min_distance = float('inf')
    nearest_location = None

    for loc in active_locations:
        distance = calculate_distance(latitude, longitude, loc.latitude, loc.longitude)
        if distance < min_distance:
            min_distance = distance
            nearest_location = loc

        # 如果在任一签到点范围内，返回成功
        if distance <= loc.radius:
            return True, loc, distance

    return False, nearest_location, min_distance


class AttendanceListCreateAPIView(LoggingMixin, generics.ListCreateAPIView):
    """考勤列表与创建

    权限控制：
    - 管理员/人事(is_staff): 查看所有人的考勤
    - 部门主管: 查看自己部门下所有人的考勤
    - 普通员工: 只能查看自己的考勤
    """
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    log_model_name = '考勤'

    # RBAC 权限
    def get_rbac_permissions(self):
        if self.request.method == 'POST':
            return [Permissions.ATTENDANCE_CREATE]
        return [Permissions.ATTENDANCE_VIEW]

    def get_queryset(self):
        qs = Attendance.objects.select_related('employee', 'employee__department').all().order_by('-date')
        user = self.request.user

        # 管理员/人事可看所有
        if user.is_staff or user.is_superuser:
            pass  # 不做过滤
        else:
            # 检查是否是部门主管
            managed_dept_ids = get_managed_department_ids(user)
            if managed_dept_ids:
                # 部门主管：可看自己部门下所有人的考勤
                qs = qs.filter(employee__department_id__in=managed_dept_ids)
            else:
                # 普通员工：只能看自己的考勤
                qs = qs.filter(employee__user=user)

        emp = self.request.query_params.get('employee')
        if emp:
            qs = qs.filter(employee__employee_id=emp)

        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            qs = qs.filter(date__gte=date_from)
        if date_to:
            qs = qs.filter(date__lte=date_to)

        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AttendanceWriteSerializer
        return AttendanceSerializer

    def get_log_detail(self, obj):
        return f'{obj.employee.employee_id} {obj.date} {obj.attendance_type}'

    def create(self, request, *args, **kwargs):
        ser = self.get_serializer(data=request.data)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        record = ser.save()
        self.log_create(request, record)
        return Response(api_success(AttendanceSerializer(record).data), status=201)


class AttendanceDetailAPIView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """考勤详情、更新、删除"""
    queryset = Attendance.objects.select_related('employee', 'employee__department').all()
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated, HasRBACPermission]
    log_model_name = '考勤'

    # RBAC 权限
    def get_rbac_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            return [Permissions.ATTENDANCE_EDIT]
        if self.request.method == 'DELETE':
            return [Permissions.ATTENDANCE_EDIT]
        return [Permissions.ATTENDANCE_VIEW]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AttendanceWriteSerializer
        return AttendanceSerializer

    def get_log_detail(self, obj):
        return f'{obj.employee.employee_id} {obj.date}'

    def update(self, request, *args, **kwargs):
        partial = request.method == 'PATCH'
        instance = self.get_object()
        ser = self.get_serializer(instance, data=request.data, partial=partial)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        rec = ser.save()
        self.log_update(request, rec)
        return Response(api_success(AttendanceSerializer(rec).data))

    def destroy(self, request, *args, **kwargs):
        rec = self.get_object()
        self.log_delete(request, rec)
        detail = self.get_log_detail(rec)
        rec.delete()
        return Response(api_success(detail=f'已删除 {detail}'))


class AttendanceCheckAPIView(views.APIView):
    """签到/签退接口"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        from django.db import IntegrityError
        import datetime

        action = request.data.get('action')
        if action not in ['check_in', 'check_out', 'update_check_out']:
            return Response(api_error('action 必须为 check_in、check_out 或 update_check_out', code='bad_action'), status=400)

        notes = request.data.get('notes') or ''
        employee_id = request.data.get('employee_id') if request.user.is_staff else None

        # 先获取员工信息
        try:
            if employee_id and request.user.is_staff:
                emp = Employee.objects.prefetch_related('checkin_locations').get(id=employee_id)
            else:
                emp = Employee.objects.prefetch_related('checkin_locations').get(user=request.user)
        except Employee.DoesNotExist:
            return Response(api_error('当前账户未关联员工', code='no_employee'), status=400)

        # 检查入职状态：待入职员工不能签到
        if emp.onboard_status != 'onboarded':
            status_text = {'pending': '待入职', 'resigned': '已离职'}.get(emp.onboard_status, '未知')
            return Response(api_error(f'您当前状态为"{status_text}"，暂不能签到', code='not_onboarded'), status=403)

        # 获取位置信息
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        # 判断需要检查的签到地点
        if emp.checkin_locations.exists():
            # 员工有关联的考勤地点
            need_location_check = emp.checkin_locations.filter(is_active=True).exists()
        else:
            # 没有关联，使用全局设置
            need_location_check = CheckInLocation.objects.filter(is_active=True).exists()

        if need_location_check:
            # 需要检查位置，必须提供位置信息
            if latitude is None or longitude is None:
                return Response(api_error('请允许获取位置信息后再签到', code='location_required'), status=400)

            try:
                latitude = float(latitude)
                longitude = float(longitude)
            except (ValueError, TypeError):
                return Response(api_error('位置信息格式错误', code='invalid_location'), status=400)

            # 位置为 0,0 表示 HTTP 环境无法获取精确位置，跳过位置检查但记录日志
            if latitude == 0 and longitude == 0:
                import logging
                logger = logging.getLogger('hr_management')
                logger.warning(f'员工 {emp.name}({emp.employee_id}) 使用默认位置(0,0)签到，可能是HTTP环境')
            else:
                # 检查是否在签到范围内
                in_range, nearest_loc, distance = check_location_in_range(latitude, longitude, employee=emp)
                if not in_range:
                    return Response(api_error(
                        f'您当前位置不在签到范围内。距离最近的签到点"{nearest_loc.name}"还有{int(distance)}米，允许范围{nearest_loc.radius}米',
                        code='out_of_range',
                        extra={'distance': int(distance), 'location': nearest_loc.name, 'radius': nearest_loc.radius}
                ), status=400)
        from ...utils import is_workday

        today = timezone.localdate()
        local_now = timezone.localtime()
        current_time = local_now.time()

        late_cutoff = datetime.time(9, 0, 0)
        early_leave_cutoff = datetime.time(18, 0, 0)

        # 判断今天是否为工作日（休息日加班不判断迟到/早退）
        is_today_workday = is_workday(today)

        try:
            rec = Attendance.objects.filter(employee=emp, date=today).first()

            if action == 'check_in':
                if not rec:
                    # 工作日9点后需要填写迟到原因，休息日加班不需要
                    is_late = is_today_workday and current_time > late_cutoff
                    if is_late and not notes.strip():
                        return Response(api_error('签到已超过 09:00，请填写迟到原因', code='reason_required'), status=400)
                    att_type = 'late' if is_late else 'check_in'
                    # 迟到时添加标签
                    formatted_notes = f'迟到原因：{notes}' if (is_late and notes) else (notes or ('加班' if not is_today_workday else ''))
                    rec = Attendance(employee=emp, date=today, attendance_type=att_type, check_in_time=current_time, notes=formatted_notes)
                    rec.save()
                    action_text = '加班签到' if not is_today_workday else '签到'
                    log_event(user=request.user, action=action_text, detail=f'{emp.employee_id} {today}', ip=get_client_ip(request))
                else:
                    if rec.check_in_time:
                        return Response(api_error('已签到，不能重复签到', code='already_checked_in'), status=400)
                    is_late = is_today_workday and current_time > late_cutoff
                    if is_late and not notes.strip():
                        return Response(api_error('签到已超过 09:00，请填写迟到原因', code='reason_required'), status=400)
                    rec.check_in_time = current_time
                    if is_late and rec.attendance_type == 'check_in':
                        rec.attendance_type = 'late'
                    if notes:
                        # 迟到时添加标签
                        rec.notes = f'迟到原因：{notes}' if is_late else notes
                    elif not is_today_workday and not rec.notes:
                        rec.notes = '加班'
                    rec.save(update_fields=['check_in_time', 'attendance_type', 'notes'])
                    log_event(user=request.user, action='补签/更新签到', detail=f'{emp.employee_id} {today}', ip=get_client_ip(request))

            elif action == 'check_out':
                if not rec:
                    return Response(api_error('尚未签到，不能签退', code='no_record'), status=400)

                is_update = rec.check_out_time is not None
                # 休息日加班不判断早退
                is_early_leave = is_today_workday and current_time < early_leave_cutoff

                # 首次签退且早退需要填写原因
                if not is_update and is_early_leave and not notes.strip():
                    return Response(api_error('签退时间早于 18:00，请填写早退原因', code='reason_required'), status=400)

                rec.check_out_time = current_time
                # 若当天已标记迟到，则不覆盖为早退/签退
                if rec.attendance_type != 'late':
                    if is_early_leave:
                        rec.attendance_type = 'early_leave'
                    elif rec.attendance_type == 'check_in':
                        rec.attendance_type = 'check_out'
                # 追加早退原因，不覆盖之前的迟到原因
                if notes:
                    formatted_note = f'早退原因：{notes}' if is_early_leave else notes
                    if rec.notes:
                        rec.notes = rec.notes + '\n' + formatted_note
                    else:
                        rec.notes = formatted_note
                rec.save(update_fields=['check_out_time', 'attendance_type', 'notes'])
                action_text = '更新签退' if is_update else '签退'
                log_event(user=request.user, action=action_text, detail=f'{emp.employee_id} {today}', ip=get_client_ip(request))

            elif action == 'update_check_out':
                if not rec:
                    return Response(api_error('尚未签到，无法更新签退时间', code='no_record'), status=400)
                if not rec.check_out_time:
                    return Response(api_error('尚未签退，请先签退', code='not_checked_out'), status=400)
                old_time = rec.check_out_time
                rec.check_out_time = current_time

                # 如果更新时间在18:00后且之前是早退，改为正常签退并清除早退原因
                if current_time >= early_leave_cutoff and rec.attendance_type == 'early_leave':
                    rec.attendance_type = 'check_out'
                    # 清除早退原因
                    if rec.notes:
                        # 移除早退原因部分，保留其他备注（如迟到原因）
                        lines = rec.notes.split('\n')
                        filtered = [line for line in lines if not line.startswith('早退原因：')]
                        rec.notes = '\n'.join(filtered).strip() or ''

                # 追加备注，不覆盖之前的原因
                if notes:
                    if rec.notes:
                        rec.notes = rec.notes + ' | ' + notes
                    else:
                        rec.notes = notes
                rec.save(update_fields=['check_out_time', 'attendance_type', 'notes'])
                log_event(user=request.user, action='更新签退时间', detail=f'{emp.employee_id} {today} {old_time}->{current_time}', ip=get_client_ip(request))

        except IntegrityError:
            rec = Attendance.objects.filter(employee=emp, date=today).first()
            if rec:
                return Response(api_error('已签到，不能重复签到', code='already_checked_in'), status=400)
            return Response(api_error('操作失败，请重试', code='db_error'), status=500)
        except Exception as e:
            return Response(api_error(f'操作失败: {str(e)}', code='error'), status=500)

        return Response(api_success(AttendanceSerializer(rec).data))


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def attendance_today(request):
    """返回当前登录用户当天考勤记录"""
    today = timezone.localdate()
    employee_param = request.query_params.get('employee')

    try:
        if request.user.is_staff and employee_param:
            emp = Employee.objects.get(employee_id=employee_param)
        else:
            emp = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return Response(api_error('当前账户未关联员工', code='no_employee'), status=400)

    rec = Attendance.objects.filter(employee=emp, date=today).first()
    data = AttendanceSerializer(rec).data if rec else None
    return Response(api_success(data))


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def attendance_workday(request):
    """检查今天是否为工作日"""
    from ...utils import is_workday, get_holiday_info

    today = timezone.localdate()
    workday = is_workday(today)
    holiday_info = get_holiday_info(today)

    holiday_name = ''
    if holiday_info:
        # type: 0工作日 1周末 2节假日 3调休补班
        if holiday_info.get('type') == 1:
            holiday_name = '周末'
        elif holiday_info.get('type') == 2:
            holiday_name = holiday_info.get('name', '节假日')

    return Response(api_success({
        'date': str(today),
        'is_workday': workday,
        'holiday_name': holiday_name,
    }))


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def attendance_my(request):
    """返回当前登录用户自己的所有考勤记录"""
    try:
        emp = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return Response(api_error('当前账户未关联员工', code='no_employee'), status=400)

    qs = Attendance.objects.filter(employee=emp).select_related('employee', 'employee__department').order_by('-date')

    # 支持日期筛选
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    if date_from:
        qs = qs.filter(date__gte=date_from)
    if date_to:
        qs = qs.filter(date__lte=date_to)

    data = AttendanceSerializer(qs, many=True).data
    return Response(api_success(data))


# ============== 补签申请相关 API ==============

@api_view(['GET', 'POST'])
@permission_classes([permissions.IsAuthenticated])
def attendance_supplement_list(request):
    """补签申请列表与创建"""
    try:
        emp = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        return Response(api_error('当前账户未关联员工', code='no_employee'), status=400)

    if request.method == 'GET':
        qs = AttendanceSupplement.objects.filter(employee=emp).order_by('-created_at')
        data = []
        for item in qs:
            data.append({
                'id': item.id,
                'date': str(item.date),
                'time': item.time.strftime('%H:%M:%S') if item.time else '',
                'type': item.supplement_type,
                'reason': item.reason,
                'status': item.status,
                'comments': item.comments,
                'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S') if item.created_at else '',
                'approved_at': item.approved_at.strftime('%Y-%m-%d %H:%M:%S') if item.approved_at else None,
            })
        return Response(api_success(data))

    elif request.method == 'POST':
        date_str = request.data.get('date')
        time_str = request.data.get('time')
        supplement_type = request.data.get('type')
        reason = request.data.get('reason', '').strip()

        if not date_str or not time_str or not supplement_type:
            return Response(api_error('请填写完整信息', code='missing_fields'), status=400)
        if not reason:
            return Response(api_error('请填写补签原因', code='reason_required'), status=400)
        if supplement_type not in ['check_in', 'check_out']:
            return Response(api_error('补签类型无效', code='invalid_type'), status=400)

        import datetime
        try:
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(api_error('日期格式无效', code='invalid_date'), status=400)

        try:
            time_obj = datetime.datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            try:
                time_obj = datetime.datetime.strptime(time_str, '%H:%M:%S').time()
            except ValueError:
                return Response(api_error('时间格式无效', code='invalid_time'), status=400)

        # 检查是否已有相同日期和类型的待审批补签申请
        existing = AttendanceSupplement.objects.filter(
            employee=emp, date=date_obj, supplement_type=supplement_type, status='pending'
        ).exists()
        if existing:
            return Response(api_error('该日期已有相同类型的待审批补签申请', code='duplicate'), status=400)

        supplement = AttendanceSupplement.objects.create(
            employee=emp,
            date=date_obj,
            time=time_obj,
            supplement_type=supplement_type,
            reason=reason,
            status='pending'
        )

        log_event(user=request.user, action='提交补签申请', detail=f'{emp.employee_id} {date_str} {supplement_type}', ip=get_client_ip(request))

        return Response(api_success({
            'id': supplement.id,
            'date': str(supplement.date),
            'time': supplement.time.strftime('%H:%M:%S'),
            'type': supplement.supplement_type,
            'reason': supplement.reason,
            'status': supplement.status,
            'created_at': supplement.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }), status=201)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def attendance_supplement_pending(request):
    """获取待审批的补签申请（管理员用）"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response(api_error('无权限', code='forbidden'), status=403)

    # 支持查询参数 status，默认只返回 pending
    status_filter = request.query_params.get('status', 'pending')

    if status_filter == 'all':
        qs = AttendanceSupplement.objects.select_related('employee').order_by('-created_at')
    else:
        qs = AttendanceSupplement.objects.filter(status=status_filter).select_related('employee').order_by('-created_at')

    data = []
    for item in qs:
        data.append({
            'id': item.id,
            'employee_id': item.employee.employee_id,
            'employee_name': item.employee.name,
            'date': str(item.date),
            'time': item.time.strftime('%H:%M:%S') if item.time else '',
            'type': item.supplement_type,
            'reason': item.reason,
            'status': item.status,
            'created_at': item.created_at.strftime('%Y-%m-%d %H:%M:%S') if item.created_at else '',
        })
    return Response(api_success(data))


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def attendance_supplement_approve(request, pk):
    """审批补签申请"""
    if not (request.user.is_staff or request.user.is_superuser):
        return Response(api_error('无权限', code='forbidden'), status=403)

    try:
        supplement = AttendanceSupplement.objects.get(pk=pk)
    except AttendanceSupplement.DoesNotExist:
        return Response(api_error('补签申请不存在', code='not_found'), status=404)

    if supplement.status != 'pending':
        return Response(api_error('该申请已处理', code='already_processed'), status=400)

    action = request.data.get('action')  # 'approve' or 'reject'
    comments = request.data.get('comments', '')

    if action not in ['approve', 'reject']:
        return Response(api_error('action 必须为 approve 或 reject', code='invalid_action'), status=400)

    supplement.status = 'approved' if action == 'approve' else 'rejected'
    supplement.approved_by = request.user
    supplement.approved_at = timezone.now()
    supplement.comments = comments
    supplement.save()

    # 如果批准，则更新考勤记录
    if action == 'approve':
        att_record, created = Attendance.objects.get_or_create(
            employee=supplement.employee,
            date=supplement.date,
            defaults={'attendance_type': 'check_in'}
        )

        if supplement.supplement_type == 'check_in':
            att_record.check_in_time = supplement.time
            if not att_record.notes:
                att_record.notes = f'补签到：{supplement.reason}'
            else:
                att_record.notes += f'\n补签到：{supplement.reason}'
        else:  # check_out
            att_record.check_out_time = supplement.time
            if not att_record.notes:
                att_record.notes = f'补签退：{supplement.reason}'
            else:
                att_record.notes += f'\n补签退：{supplement.reason}'

        att_record.save()
        log_event(user=request.user, action='批准补签申请', detail=f'{supplement.employee.employee_id} {supplement.date}', ip=get_client_ip(request))
    else:
        log_event(user=request.user, action='拒绝补签申请', detail=f'{supplement.employee.employee_id} {supplement.date}', ip=get_client_ip(request))

    return Response(api_success({'status': supplement.status, 'comments': supplement.comments}))


# ============== 签到地点管理 API ==============

class CheckInLocationListCreateAPIView(LoggingMixin, generics.ListCreateAPIView):
    """签到地点列表与创建"""
    queryset = CheckInLocation.objects.all()
    serializer_class = CheckInLocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    log_model_name = '签到地点'

    def get_queryset(self):
        qs = CheckInLocation.objects.all().order_by('-is_default', '-created_at')
        # 普通用户只能看到启用的签到地点
        if not self.request.user.is_staff:
            qs = qs.filter(is_active=True)
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CheckInLocationWriteSerializer
        return CheckInLocationSerializer

    def get_log_detail(self, obj):
        return f'{obj.name} ({obj.address})'

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(api_error('无权限', code='forbidden'), status=403)

        ser = self.get_serializer(data=request.data)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        location = ser.save()
        self.log_create(request, location)
        return Response(api_success(CheckInLocationSerializer(location).data), status=201)


class CheckInLocationDetailAPIView(LoggingMixin, generics.RetrieveUpdateDestroyAPIView):
    """签到地点详情、更新、删除"""
    queryset = CheckInLocation.objects.all()
    serializer_class = CheckInLocationSerializer
    permission_classes = [permissions.IsAuthenticated]
    log_model_name = '签到地点'

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CheckInLocationWriteSerializer
        return CheckInLocationSerializer

    def get_log_detail(self, obj):
        return f'{obj.name} ({obj.address})'

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(api_error('无权限', code='forbidden'), status=403)

        partial = request.method == 'PATCH'
        instance = self.get_object()
        ser = self.get_serializer(instance, data=request.data, partial=partial)
        if not ser.is_valid():
            return Response(api_error('验证失败', errors=ser.errors), status=400)
        location = ser.save()
        self.log_update(request, location)
        return Response(api_success(CheckInLocationSerializer(location).data))

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(api_error('无权限', code='forbidden'), status=403)

        location = self.get_object()
        self.log_delete(request, location)
        detail = self.get_log_detail(location)
        location.delete()
        return Response(api_success(detail=f'已删除签到地点 {detail}'))


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def checkin_locations_active(request):
    """获取所有启用的签到地点（用于前端显示）"""
    locations = CheckInLocation.objects.filter(is_active=True).order_by('-is_default', 'name')
    data = CheckInLocationSerializer(locations, many=True).data
    return Response(api_success(data))


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def attendance_alerts(request):
    """获取考勤异常记录（缺勤、迟到、早退）
    - 人事/管理员：显示所有员工的异常记录
    - 部门主管：显示自己部门下的异常记录
    - 普通员工：只显示自己的异常记录
    """
    from datetime import timedelta

    days = int(request.query_params.get('days', 7))
    days = max(1, min(days, 180))
    alert_type = request.query_params.get('type', None)

    since = timezone.localdate() - timedelta(days=days)

    # 查询异常考勤记录（仅查询已入职员工）
    qs = Attendance.objects.filter(
        date__gte=since,
        attendance_type__in=['absent', 'late', 'early_leave'],
        employee__onboard_status='onboarded',
    ).select_related('employee', 'employee__department', 'employee__position').order_by('-date', '-id')

    # 根据权限过滤
    user = request.user
    if not user.is_staff:
        # 非人事账号
        try:
            employee = Employee.objects.get(user=user)
            # 检查是否是部门主管
            managed_dept_ids = get_managed_department_ids(user)
            if managed_dept_ids:
                # 部门主管：看自己部门下的异常记录
                qs = qs.filter(employee__department_id__in=managed_dept_ids)
            else:
                # 普通员工：只看自己的异常记录
                qs = qs.filter(employee=employee)
        except Employee.DoesNotExist:
            qs = qs.none()

    if alert_type:
        qs = qs.filter(attendance_type=alert_type)

    data = []
    for att in qs[:100]:  # 限制最多100条
        data.append({
            'id': att.id,
            'date': str(att.date),
            'attendance_type': att.attendance_type,
            'check_in_time': att.check_in_time.isoformat() if att.check_in_time else None,
            'check_out_time': att.check_out_time.isoformat() if att.check_out_time else None,
            'notes': att.notes,
            'employee': {
                'id': att.employee.id,
                'name': att.employee.name,
                'employee_id': att.employee.employee_id,
                'department': {
                    'id': att.employee.department.id,
                    'name': att.employee.department.name,
                } if att.employee.department else None,
            }
        })

    return Response(api_success(data))

