# 密钥轮换清单（泄露应急）

适用场景：`.env` 曾误入公开仓库历史，需要立刻完成凭证轮换与会话失效。

## 0. 立即止血（已完成）

1. `.env` 已从当前分支移除并加入忽略。
2. 公开仓库已执行历史重写并强推。

## 1. 高优先级（30 分钟内）

1. 轮换 Django `SECRET_KEY`。
2. 修改 PostgreSQL 账号密码（建议同时更换用户名）。
3. 更新 `DATABASE_URL` 对应凭证。
4. 轮换邮箱 SMTP 授权码（`EMAIL_HOST_PASSWORD`）。
5. 轮换高德地图 Key：`VITE_AMAP_KEY` 与 `VITE_AMAP_SECURITY_JS_CODE`。

## 2. 中优先级（当天完成）

1. 若 Redis 使用了鉴权，轮换 Redis 密码并更新 `REDIS_URL`。
2. 重新签发对外 API 访问密钥（如有自定义三方集成）。
3. 检查服务器上是否存在旧 `.env` 备份或日志泄露。

## 3. Django 会话与令牌失效

在更新 `SECRET_KEY` 后，旧签名令牌会自然失效；如需强制立即失效可执行：

```powershell
# 失效 Django session（如使用数据库 session）
python manage.py shell -c "from django.contrib.sessions.models import Session; Session.objects.all().delete()"
```

如果使用 JWT 黑名单机制，建议把在泄露时间窗口内签发的 refresh token 全部拉黑或清空相关存储。

## 4. 数据库凭证轮换建议（PostgreSQL）

```sql
-- 示例：仅演示流程，请按你实际账号替换
ALTER USER hr_user WITH PASSWORD 'new-strong-password';
```

随后同步更新所有部署环境变量：

1. 服务器 `.env` / Secret 管理系统
2. Docker Compose 环境变量
3. CI/CD 平台变量

## 5. 验收清单

1. 应用可正常登录、查询、写入。
2. 邮件验证码发送正常。
3. 地图定位功能正常。
4. 数据库连接池无认证错误。
5. 公开仓库默认分支不存在 `.env` 文件。
6. 公开仓库历史路径中无 `.env` 提交记录。

## 6. 后续加固建议

1. 在 GitHub 仓库开启 Secret scanning 与 Push protection（若可用）。
2. 在 CI 增加泄露检测（如 gitleaks/trufflehog）。
3. 统一采用 `.env.example` / `.env.production.example` 模板，不提交真实凭证。
4. 把生产凭证迁移到专用密钥管理服务（如云 KMS / Secrets Manager）。
