from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('hr_management', '0009_salaryrecord_paid_salaryrecord_paid_at_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='leaverequest',
            name='resignation_hr_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='人事审批时间'),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='resignation_hr_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resignation_hr_reviews', to=settings.AUTH_USER_MODEL, verbose_name='人事审批人'),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='resignation_hr_comment',
            field=models.TextField(blank=True, verbose_name='人事意见'),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='resignation_hr_status',
            field=models.CharField(choices=[('pending', '待处理'), ('approved', '已同意'), ('rejected', '已拒绝')], default='pending', max_length=20, verbose_name='人事审批状态'),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='resignation_manager_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='直属上级审批时间'),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='resignation_manager_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resignation_manager_reviews', to=settings.AUTH_USER_MODEL, verbose_name='直属上级审批人'),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='resignation_manager_comment',
            field=models.TextField(blank=True, verbose_name='直属上级意见'),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='resignation_manager_status',
            field=models.CharField(choices=[('pending', '待处理'), ('approved', '已同意'), ('rejected', '已拒绝')], default='pending', max_length=20, verbose_name='直属上级审批状态'),
        ),
    ]
