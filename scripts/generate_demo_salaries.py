import argparse
import os
import sys
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
os.environ.setdefault('DISABLE_SCHEDULER', 'true')

import django

django.setup()

from django.core.cache import cache
from django.utils import timezone

from hr_management.models import Employee, SalaryRecord
from hr_management.services import CacheKeys


DEFAULT_MONTH_CONFIG = {
    2: {'paid': True, 'paid_at': '2026-03-08T10:00:00'},
    3: {'paid': False, 'paid_at': None},
}


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def make_paid_at(value: str | None):
    if not value:
        return None
    naive = datetime.fromisoformat(value)
    return timezone.make_aware(naive, timezone.get_current_timezone())


def build_demo_amounts(employee: Employee, month: int) -> tuple[Decimal, Decimal, Decimal]:
    base_salary = money(employee.salary or Decimal('0'))
    bonus_ratio = Decimal('0.03') + Decimal(employee.id % 4) * Decimal('0.005')
    bonus = money(base_salary * bonus_ratio + Decimal(80 + month * 10 + (employee.id % 3) * 30))
    allowance = money(Decimal(120 + (employee.id % 5) * 35 + month * 8))
    return base_salary, bonus, allowance


def ensure_demo_salaries(year: int, months: list[int]) -> None:
    employees = list(
        Employee.objects.filter(is_active=True, onboard_status='onboarded').order_by('id')
    )
    if not employees:
        raise RuntimeError('没有可用于生成演示薪资的在职员工')

    print(f'active_employees={len(employees)}')

    for month in months:
        config = DEFAULT_MONTH_CONFIG.get(month, {'paid': False, 'paid_at': None})
        paid_at = make_paid_at(config['paid_at'])
        created = 0
        updated = 0
        skipped = 0

        for employee in employees:
            record = SalaryRecord.objects.filter(employee=employee, year=year, month=month).first()
            if record:
                should_save = False
                if config['paid'] and not record.paid:
                    record.paid = True
                    record.paid_at = paid_at
                    should_save = True

                if should_save:
                    record.save(update_fields=['paid', 'paid_at'])
                    updated += 1
                else:
                    skipped += 1
                continue

            base_salary, bonus, allowance = build_demo_amounts(employee, month)
            SalaryRecord.objects.create(
                employee=employee,
                year=year,
                month=month,
                basic_salary=base_salary,
                bonus=bonus,
                overtime_pay=Decimal('0.00'),
                allowance=allowance,
                paid=config['paid'],
                paid_at=paid_at,
            )
            created += 1

        month_total = SalaryRecord.objects.filter(year=year, month=month).count()
        paid_total = SalaryRecord.objects.filter(year=year, month=month, paid=True).count()
        print(
            f'month={year}-{month:02d} created={created} updated={updated} '
            f'skipped={skipped} total={month_total} paid={paid_total}'
        )

    cache.delete(CacheKeys.DASHBOARD_SUMMARY)
    print(f'cache_cleared={CacheKeys.DASHBOARD_SUMMARY}')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='为演示环境生成指定月份的薪资记录')
    parser.add_argument('--year', type=int, default=2026)
    parser.add_argument('--months', type=int, nargs='+', default=[2, 3])
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    ensure_demo_salaries(args.year, args.months)
