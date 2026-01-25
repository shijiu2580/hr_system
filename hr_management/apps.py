from django.apps import AppConfig


class HrManagementConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hr_management'
    verbose_name = '人事管理系统'

    def ready(self):
        """应用启动时注册信号处理器"""
        # 导入信号处理器以注册它们
        from . import signals  # noqa: F401

        # 启动简易调度器，处理每日缺勤标记等后台任务
        # 开发环境可设置环境变量 DISABLE_SCHEDULER=True 禁用
        import os
        if os.environ.get('DISABLE_SCHEDULER', '').lower() == 'true':
            return
        
        try:
            from .tasks import scheduler, setup_scheduled_tasks

            setup_scheduled_tasks()
            scheduler.start()
        except Exception:
            # 避免启动失败阻断应用，可在日志中查看详细错误
            import logging

            logging.getLogger(__name__).exception('Failed to start scheduler')
