import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_system.settings')
os.environ.setdefault('DISABLE_SCHEDULER', 'true')

import django

django.setup()

from django.apps import apps
from django.core.management.color import no_style
from django.db import connection


def main() -> None:
    statements = connection.ops.sequence_reset_sql(no_style(), apps.get_models())
    with connection.cursor() as cursor:
        for statement in statements:
            cursor.execute(statement)
    print(f"reset_sequences={len(statements)}")


if __name__ == '__main__':
    main()
