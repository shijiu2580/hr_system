from django.core.management.base import BaseCommand
from django.utils import timezone
from hr_management.models import SalaryRecord


def _previous_year_month(dt):
    if dt.month == 1:
        return dt.year - 1, 12
    return dt.year, dt.month - 1

class Command(BaseCommand):
    help = "在每月5号发薪：默认发放上个月工资，标记对应月份记录为已发薪并记录时间。可选 --year --month 参数"

    def add_arguments(self, parser):
        parser.add_argument('--year', type=int, help='年份，默认当前年份')
        parser.add_argument('--month', type=int, help='月份(1-12)，默认当前月份')
        parser.add_argument('--dry-run', action='store_true', help='试运行，仅统计不落库')

    def handle(self, *args, **options):
        now = timezone.localtime()
        default_year, default_month = _previous_year_month(now)
        year = options.get('year') or default_year
        month = options.get('month') or default_month
        dry_run = options.get('dry_run') or False

        qs = SalaryRecord.objects.filter(year=year, month=month, paid=False)
        count = qs.count()
        if dry_run:
            self.stdout.write(self.style.WARNING(f"试运行：待发薪记录 {count} 条（{year}-{month}）"))
            return

        paid_time = timezone.now()
        updated = qs.update(paid=True, paid_at=paid_time)
        self.stdout.write(self.style.SUCCESS(f"已标记发薪：{updated} 条（{year}-{month}，时间 {paid_time}）"))
        if updated == 0:
            self.stdout.write(self.style.WARNING(
                "未找到可发放记录：可能该月份工资未生成，或已发放（paid=True）。"
            ))
