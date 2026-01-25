from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
import secrets


class Command(BaseCommand):
    help = '重置指定用户名的密码，若未提供新密码则自动生成随机强密码。\n示例: python manage.py reset_password admin 或 python manage.py reset_password admin --password=NewPass123'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='要重置的用户名')
        parser.add_argument('--password', type=str, default=None, help='指定新密码，留空则自动生成强密码')
        parser.add_argument('--show-only', action='store_true', help='仅生成随机密码但不写入（调试用）')

    def handle(self, *args, **options):
        username = options['username']
        raw_password = options['password']
        show_only = options['show_only']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'用户 {username} 不存在')

        # 自动生成随机密码
        if not raw_password:
            # 生成 16 字符 URL-safe 随机字符串，再补强 2 个特殊字符
            rand_core = secrets.token_urlsafe(12)  # 约 16 字符
            raw_password = rand_core + '!A'

        if show_only:
            self.stdout.write(self.style.WARNING(f'仅展示随机密码（未写入）：{raw_password}'))
            return

        user.set_password(raw_password)
        user.save(update_fields=['password'])
        self.stdout.write(self.style.SUCCESS(f'用户 {username} 密码已重置: {raw_password}'))
        self.stdout.write('请及时使用此密码登录并在前端或后台修改为符合策略的专用密码。')
