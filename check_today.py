import django, os
os.environ['DJANGO_SETTINGS_MODULE'] = 'hr_system.settings'
django.setup()

from hr_management.models import Attendance, Employee
from datetime import date

emp = Employee.objects.filter(user__username='admin').first()
print('Employee:', emp, emp.id if emp else None)

recs = Attendance.objects.filter(employee=emp, date=date.today())
print('Records count:', recs.count())

for r in recs:
    print(f'  id={r.id} check_in={r.check_in_time} check_out={r.check_out_time} type={r.attendance_type} notes={r.notes}')

if not emp:
    print('No admin employee found!')
    emps = Employee.objects.all()[:5]
    for e in emps:
        print(f'  employee: {e.user.username} id={e.id}')
