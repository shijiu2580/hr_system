"""
异步任务模块 - 使用 Django-Q 或 Celery 的轻量级替代方案

对于简单场景，使用线程池执行后台任务；
对于生产环境，建议配置 Redis 或 Celery
"""
import threading
import logging
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Callable, Any, Dict, Optional
from functools import wraps
from queue import Queue
import time
from datetime import timedelta, date

from django.conf import settings
from django.core.mail import send_mail
from django.db import connection
from django.utils import timezone


logger = logging.getLogger('hr_management.tasks')


# 全局线程池
_executor: Optional[ThreadPoolExecutor] = None
_task_queue: Queue = Queue()


def get_executor() -> ThreadPoolExecutor:
    """获取或创建线程池"""
    global _executor
    if _executor is None:
        max_workers = getattr(settings, 'TASK_EXECUTOR_MAX_WORKERS', 4)
        _executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix='async_task_')
    return _executor


def shutdown_executor():
    """关闭线程池（应用关闭时调用）"""
    global _executor
    if _executor:
        _executor.shutdown(wait=True)
        _executor = None


class TaskResult:
    """任务结果包装器"""

    def __init__(self, task_id: str, future: Future):
        self.task_id = task_id
        self.future = future
        self.created_at = time.time()

    @property
    def is_done(self) -> bool:
        return self.future.done()

    @property
    def is_successful(self) -> bool:
        if not self.is_done:
            return False
        try:
            self.future.result()
            return True
        except Exception:
            return False

    def get_result(self, timeout: float = None):
        """获取结果（阻塞）"""
        return self.future.result(timeout=timeout)

    def get_exception(self) -> Optional[Exception]:
        """获取异常"""
        if not self.is_done:
            return None
        try:
            self.future.result()
            return None
        except Exception as e:
            return e


def async_task(func: Callable) -> Callable:
    """
    异步任务装饰器 - 将函数提交到线程池执行

    Example:
        @async_task
        def send_notification(user_id, message):
            ...

        # 调用时会立即返回
        result = send_notification(user_id=1, message='Hello')

        # 等待结果
        result.get_result()
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> TaskResult:
        task_id = f"{func.__name__}_{int(time.time() * 1000)}"

        def task_wrapper():
            # 确保数据库连接在任务完成后关闭
            try:
                logger.info(f"Task {task_id} started")
                result = func(*args, **kwargs)
                logger.info(f"Task {task_id} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Task {task_id} failed: {e}")
                raise
            finally:
                connection.close()

        future = get_executor().submit(task_wrapper)
        return TaskResult(task_id, future)

    # 添加同步执行方法
    wrapper.sync = func
    return wrapper


def delay_task(delay_seconds: float):
    """
    延迟任务装饰器

    Example:
        @delay_task(60)  # 延迟60秒执行
        def cleanup_temp_files():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> TaskResult:
            task_id = f"{func.__name__}_{int(time.time() * 1000)}"

            def delayed_task():
                time.sleep(delay_seconds)
                try:
                    connection.ensure_connection()
                    return func(*args, **kwargs)
                finally:
                    connection.close()

            future = get_executor().submit(delayed_task)
            return TaskResult(task_id, future)

        wrapper.sync = func
        return wrapper

    return decorator


# ============ 预定义的异步任务 ============

@async_task
def send_email_async(
    subject: str,
    message: str,
    recipient_list: list,
    html_message: str = None
):
    """异步发送邮件"""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else None,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Email sent to {recipient_list}")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        raise


@async_task
def log_user_action(
    user_id: int,
    action: str,
    detail: str = None,
    ip_address: str = None
):
    """异步记录用户操作日志"""
    from .models import SystemLog
    from django.contrib.auth.models import User

    try:
        user = User.objects.get(id=user_id) if user_id else None
        SystemLog.objects.create(
            user=user,
            action=action,
            detail=detail or '',
            ip_address=ip_address or '',
            level='INFO'
        )
    except Exception as e:
        logger.error(f"Failed to log user action: {e}")


@async_task
def generate_report_async(
    report_type: str,
    params: Dict[str, Any],
    user_id: int
):
    """
    异步生成报表

    Args:
        report_type: 报表类型
        params: 报表参数
        user_id: 请求用户ID
    """
    from .query_utils import ReportQueries

    logger.info(f"Generating report: {report_type} for user {user_id}")

    report_generators = {
        'attendance': ReportQueries.get_attendance_summary,
        'salary': ReportQueries.get_salary_statistics,
        'department': ReportQueries.get_department_statistics,
    }

    generator = report_generators.get(report_type)
    if not generator:
        raise ValueError(f"Unknown report type: {report_type}")

    # 生成报表数据
    data = generator(**params)

    # 这里可以保存到文件或发送通知
    logger.info(f"Report {report_type} generated successfully")
    return data


@async_task
def cleanup_old_logs(days: int = 90):
    """清理旧日志"""
    from .models import SystemLog
    from django.utils import timezone
    from datetime import timedelta

    cutoff = timezone.now() - timedelta(days=days)
    count, _ = SystemLog.objects.filter(timestamp__lt=cutoff).delete()
    logger.info(f"Cleaned up {count} old log entries")
    return count


@async_task
def backup_database_async():
    """异步数据库备份"""
    import shutil
    from pathlib import Path
    from django.utils import timezone

    db_path = Path(settings.DATABASES['default']['NAME'])
    if not db_path.exists():
        raise FileNotFoundError("Database file not found")

    backup_dir = Path(settings.MEDIA_ROOT) / 'backups'
    backup_dir.mkdir(parents=True, exist_ok=True)

    ts = timezone.now().strftime('%Y%m%d_%H%M%S')
    backup_path = backup_dir / f'backup_{ts}.sqlite3'

    shutil.copy2(db_path, backup_path)
    logger.info(f"Database backed up to {backup_path}")
    return str(backup_path)


@async_task
def sync_employee_data(employee_id: int):
    """同步员工数据（示例任务）"""
    from .models import Employee

    try:
        employee = Employee.objects.get(id=employee_id)
        # 这里可以添加与外部系统同步的逻辑
        logger.info(f"Synced employee {employee.name}")
    except Employee.DoesNotExist:
        logger.warning(f"Employee {employee_id} not found")


@async_task
def mark_absent_for_date(target_date=None):
    """为未签到的员工生成缺勤记录

    逻辑：
    - 默认处理昨天的数据
    - 如果是当天且已过18:00，也可以处理当天数据
    - 节假日/周末跳过
    - 已请假/出差的员工跳过
    """
    from django.db.models import Q
    from .models import Attendance, Employee, LeaveRequest, BusinessTrip
    from .utils import is_workday
    import datetime

    today = timezone.localdate()
    now_time = timezone.localtime().time()
    absent_cutoff = datetime.time(18, 0, 0)  # 18:00后未签到算缺勤

    # 默认处理昨天，如果没有指定日期
    if target_date is None:
        target_date = today - timedelta(days=1)

    # 使用节假日API判断是否为工作日（包含调休补班支持）
    if not is_workday(target_date):
        logger.info("Skip marking absent for non-workday %s", target_date)
        return {'date': str(target_date), 'created': 0, 'skipped': 0}

    # 时间检查逻辑
    if target_date > today:
        # 未来日期，跳过
        logger.info("Skip marking absent for future date %s", target_date)
        return {'date': str(target_date), 'created': 0, 'skipped': 0}
    elif target_date == today:
        # 当天数据：必须过了18:00才处理
        if now_time < absent_cutoff:
            logger.info("Skip marking absent for today %s (before 18:00)", target_date)
            return {'date': str(target_date), 'created': 0, 'skipped': 0, 'reason': 'before_cutoff'}
    # 过去日期直接处理

    # 仅处理已入职且在职的员工（排除待入职员工）
    active_employees = Employee.objects.filter(
        is_active=True,
        onboard_status='onboarded'
    ).filter(
        Q(hire_date__lte=target_date) | Q(hire_date__isnull=True)
    )

    existing_ids = set(
        Attendance.objects.filter(date=target_date).values_list('employee_id', flat=True)
    )
    leave_ids = set(
        LeaveRequest.objects.filter(
            status='approved', start_date__lte=target_date, end_date__gte=target_date
        ).values_list('employee_id', flat=True)
    )
    trip_ids = set(
        BusinessTrip.objects.filter(
            status='approved', start_date__lte=target_date, end_date__gte=target_date
        ).values_list('employee_id', flat=True)
    )

    skip_ids = existing_ids | leave_ids | trip_ids
    to_create = active_employees.exclude(id__in=skip_ids)

    created = 0
    for emp in to_create:
        _, created_flag = Attendance.objects.get_or_create(
            employee=emp,
            date=target_date,
            defaults={
                'attendance_type': 'absent',
                'notes': '全天未签到，自动标记缺勤',
            }
        )
        if created_flag:
            created += 1

    logger.info("Marked %s employees absent for %s", created, target_date)
    return {'date': str(target_date), 'created': created, 'skipped': len(skip_ids)}


@async_task
def mark_absent_today():
    """标记当天缺勤（18:00后执行）"""
    today = timezone.localdate()
    return mark_absent_for_date.sync(today)


# ============ 自动发薪任务 ============

@async_task
def auto_disburse_salary(year: int = None, month: int = None):
    """
    自动发放指定月份的薪资

    默认发放上个月的薪资（每月5号执行）
    """
    from .models import SalaryRecord, SystemLog
    from .notifications import notify_salary_issued
    from django.contrib.auth import get_user_model

    User = get_user_model()

    # 默认发放上个月薪资
    if year is None or month is None:
        today = timezone.localdate()
        if today.month == 1:
            year = today.year - 1
            month = 12
        else:
            year = today.year
            month = today.month - 1

    # 查询待发放记录
    records = SalaryRecord.objects.filter(year=year, month=month, paid=False)

    if not records.exists():
        logger.info(f"No pending salary records for {year}-{month:02d}")
        return {'year': year, 'month': month, 'count': 0, 'message': '无待发放记录'}

    count = records.count()
    now = timezone.now()

    # 获取发放记录的ID列表（在update前获取）
    record_ids = list(records.values_list('id', flat=True))

    # 批量更新为已发放
    records.update(paid=True, paid_at=now)

    # 发送通知给每位员工
    notified = 0
    for record in SalaryRecord.objects.filter(id__in=record_ids).select_related('employee', 'employee__user'):
        if record.employee.user:
            try:
                notify_salary_issued(
                    record.employee.user,
                    f'{record.year}年{record.month}月',
                    float(record.net_salary)
                )
                notified += 1
            except Exception as e:
                logger.warning(f"Failed to notify {record.employee.name}: {e}")

    # 记录系统日志（使用系统用户）
    try:
        system_user = User.objects.filter(is_superuser=True).first()
        SystemLog.objects.create(
            user=system_user,
            action='自动发薪',
            detail=f'自动发放 {year}年{month}月 薪资：{count}人，通知{notified}人'
        )
    except Exception as e:
        logger.warning(f"Failed to create system log: {e}")

    logger.info(f"Auto disbursed salary for {year}-{month:02d}: {count} records, {notified} notified")
    return {
        'year': year,
        'month': month,
        'count': count,
        'notified': notified,
        'paid_at': now.isoformat()
    }


def check_and_disburse_salary():
    """
    检查是否需要发放薪资（每月5号自动执行）

    发薪日配置可通过 settings.SALARY_DISBURSE_DAY 设置，默认为5
    """
    today = timezone.localdate()
    disburse_day = getattr(settings, 'SALARY_DISBURSE_DAY', 5)

    if today.day != disburse_day:
        logger.debug(f"Today is {today.day}, not salary disburse day ({disburse_day})")
        return None

    logger.info(f"Today is salary disburse day ({disburse_day}), running auto disburse...")
    return auto_disburse_salary.sync()


# ============ 自动创建薪资条任务 ============

@async_task
def auto_generate_salary_records(year: int = None, month: int = None):
    """
    自动为所有在职员工生成薪资条

    默认生成上个月的薪资条（每月1号执行）
    薪资计算规则：
    - 基本工资：取员工档案中的 salary 字段
    - 奖金/津贴/加班费：默认为0，需要HR手动调整
    """
    from .models import SalaryRecord, Employee, SystemLog
    from django.contrib.auth import get_user_model
    from decimal import Decimal

    User = get_user_model()

    # 默认生成上个月薪资条
    if year is None or month is None:
        today = timezone.localdate()
        if today.month == 1:
            year = today.year - 1
            month = 12
        else:
            year = today.year
            month = today.month - 1

    # 获取所有在职员工（已入职状态）
    active_employees = Employee.objects.filter(
        is_active=True,
        onboard_status='onboarded'
    )

    created_count = 0
    skipped_count = 0

    for emp in active_employees:
        # 检查是否已存在该月薪资记录
        if SalaryRecord.objects.filter(employee=emp, year=year, month=month).exists():
            skipped_count += 1
            continue

        # 获取基本工资（从员工档案）
        basic_salary = emp.salary or Decimal('0')

        # 创建薪资记录
        SalaryRecord.objects.create(
            employee=emp,
            year=year,
            month=month,
            basic_salary=basic_salary,
            bonus=Decimal('0'),
            overtime_pay=Decimal('0'),
            allowance=Decimal('0'),
            paid=False
        )
        created_count += 1

    # 记录系统日志
    try:
        system_user = User.objects.filter(is_superuser=True).first()
        SystemLog.objects.create(
            user=system_user,
            action='自动生成薪资条',
            detail=f'自动生成 {year}年{month}月 薪资条：新建{created_count}条，跳过{skipped_count}条（已存在）'
        )
    except Exception as e:
        logger.warning(f"Failed to create system log: {e}")

    logger.info(f"Auto generated salary records for {year}-{month:02d}: created {created_count}, skipped {skipped_count}")
    return {
        'year': year,
        'month': month,
        'created': created_count,
        'skipped': skipped_count
    }


def check_and_generate_salary():
    """
    检查是否需要生成薪资条（每月1号自动执行）

    生成日配置可通过 settings.SALARY_GENERATE_DAY 设置，默认为1
    """
    today = timezone.localdate()
    generate_day = getattr(settings, 'SALARY_GENERATE_DAY', 1)

    if today.day != generate_day:
        logger.debug(f"Today is {today.day}, not salary generate day ({generate_day})")
        return None

    logger.info(f"Today is salary generate day ({generate_day}), running auto generate...")
    return auto_generate_salary_records.sync()


# ============ 定时任务调度器（简化版）============

class SimpleScheduler:
    """
    简单的定时任务调度器

    对于生产环境，建议使用 Celery Beat 或 APScheduler
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._tasks: Dict[str, Dict] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._initialized = True

    def register(self, name: str, func: Callable, interval_seconds: int):
        """注册定时任务"""
        self._tasks[name] = {
            'func': func,
            'interval': interval_seconds,
            'last_run': 0,
        }
        logger.info(f"Registered scheduled task: {name} (every {interval_seconds}s)")

    def start(self):
        """启动调度器"""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Scheduler started")

    def stop(self):
        """停止调度器"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Scheduler stopped")

    def _run_loop(self):
        """调度循环"""
        while self._running:
            current_time = time.time()

            for name, task in self._tasks.items():
                if current_time - task['last_run'] >= task['interval']:
                    try:
                        logger.debug(f"Running scheduled task: {name}")
                        get_executor().submit(task['func'])
                        task['last_run'] = current_time
                    except Exception as e:
                        logger.error(f"Scheduled task {name} failed: {e}")

            time.sleep(1)  # 每秒检查一次


# 全局调度器实例
scheduler = SimpleScheduler()


def setup_scheduled_tasks():
    """设置定时任务"""
    # 每天凌晨清理旧日志
    scheduler.register('cleanup_logs', lambda: cleanup_old_logs.sync(90), 86400)

    # 每天补齐缺勤记录，默认处理前一天（兜底）
    scheduler.register('mark_absent_daily', lambda: mark_absent_for_date.sync(None), 86400)

    # 每小时检查当天缺勤（18:00后生效）
    scheduler.register('mark_absent_today', lambda: mark_absent_today.sync(), 3600)

    # 每小时刷新缓存
    scheduler.register('refresh_cache', _refresh_cache, 3600)

    # 每天检查是否为生成薪资条日（每天执行一次，1号时自动生成）
    scheduler.register('auto_generate_salary', check_and_generate_salary, 86400)

    # 每天检查是否为发薪日（每天执行一次，5号时自动发薪）
    scheduler.register('auto_disburse_salary', check_and_disburse_salary, 86400)


def _refresh_cache():
    """刷新常用缓存"""
    from .services import CacheManager
    CacheManager.warm_cache()
