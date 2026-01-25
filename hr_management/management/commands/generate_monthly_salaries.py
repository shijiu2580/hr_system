from django.core.management.base import BaseCommand
from django.utils import timezone
from hr_management.models import Employee, SalaryRecord
from decimal import Decimal

class Command(BaseCommand):
    help = "为在职员工生成当月薪资记录（避免重复）。可选 --year --month 参数"

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, help='年份，默认当前年份')
        parser.add_argument('--month', type=int, help='月份(1-12)，默认当前月份')
        parser.add_argument('--include-inactive', action='store_true', help='是否包含离职员工，默认不包含')

    def handle(self, *args, **options):
        now = timezone.localtime()
        year = options.get('year') or now.year
        month = options.get('month') or now.month
        include_inactive = options.get('include_inactive') or False

        qs = Employee.objects.all()
        if not include_inactive:
            qs = qs.filter(is_active=True)

        created_count = 0
        skipped_count = 0

        for emp in qs.iterator():
            # 基本工资为空则视为0
            basic = Decimal(emp.salary or 0)
            # 若已存在该员工当月记录，跳过
            exists = SalaryRecord.objects.filter(employee=emp, year=year, month=month).exists()
            if exists:
                skipped_count += 1
                continue
            SalaryRecord.objects.create(
                employee=emp,
                year=year,
                month=month,
                basic_salary=basic,
                bonus=Decimal('0'),
                overtime_pay=Decimal('0'),
                allowance=Decimal('0'),
            )
            created_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"生成完成：新建 {created_count} 条，跳过 {skipped_count} 条（{year}-{month}）"
        ))
