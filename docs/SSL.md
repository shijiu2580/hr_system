# HTTPS / SSL 证书配置指南

## 🔐 概述

本项目使用 **Let's Encrypt** 免费 SSL 证书，通过 **Certbot** 自动申请和续期。

本文件仅针对生产环境。当前本地开发默认不启用 HTTPS，而是直接使用：
- Web: `http://localhost:5173`
- Mobile: `http://localhost:5174`
- API: `http://127.0.0.1:8000`

Docker / Nginx 场景下对外映射端口为：
- Web: `3000`
- Mobile: `3001`
- API: `8000`

## 📋 域名列表

| 域名 | 用途 |
|------|------|
| canway.site | Web 前端 |
| www.canway.site | Web 前端 (别名) |
| m.canway.site | 移动端 H5 |
| api.canway.site | API 后端 |

## 🚀 快速部署

### 1. 首次配置 (服务器上执行)

```bash
# 上传脚本到服务器
scp scripts/ssl_setup.sh root@159.75.138.185:/root/

# SSH 登录服务器
ssh root@159.75.138.185

# 执行安装
chmod +x ssl_setup.sh
./ssl_setup.sh install
```

### 2. 更新 Nginx 配置

```bash
# 复制配置文件
cp nginx/canway.site.conf /etc/nginx/sites-available/
ln -sf /etc/nginx/sites-available/canway.site.conf /etc/nginx/sites-enabled/

# 测试并重载
nginx -t && systemctl reload nginx
```

## 📝 手动操作

### 申请证书

```bash
# 使用 Nginx 插件 (推荐)
certbot --nginx -d canway.site -d www.canway.site -d m.canway.site -d api.canway.site

# 或使用 Standalone 模式 (需要先停止 Nginx)
certbot certonly --standalone -d canway.site -d www.canway.site -d m.canway.site -d api.canway.site
```

### 续期证书

```bash
# 测试续期 (不实际执行)
certbot renew --dry-run

# 强制续期
certbot renew --force-renewal

# 重载 Nginx 使证书生效
systemctl reload nginx
```

### 查看证书状态

```bash
certbot certificates
```

## 📂 证书位置

```
/etc/letsencrypt/live/canway.site/
├── fullchain.pem    # 完整证书链 (包含中间证书)
├── privkey.pem      # 私钥
├── cert.pem         # 域名证书
└── chain.pem        # 中间证书
```

## ⏰ 自动续期

Let's Encrypt 证书有效期 90 天，Certbot 会自动配置续期任务：

```bash
# 查看定时任务
systemctl list-timers | grep certbot

# 或查看 cron
crontab -l | grep certbot
```

续期成功后会自动执行：
```bash
/etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
```

## 🔧 故障排除

### 证书申请失败

1. **检查 DNS 解析**
   ```bash
   dig canway.site +short
   dig m.canway.site +short
   ```

2. **检查 80 端口是否开放**
   ```bash
   curl -I http://canway.site/.well-known/acme-challenge/test
   ```

3. **检查防火墙**
   ```bash
   # 腾讯云需要在安全组开放 80 和 443 端口
   ufw allow 80
   ufw allow 443
   ```

### 证书过期

```bash
# 查看过期时间
openssl x509 -in /etc/letsencrypt/live/canway.site/fullchain.pem -noout -dates

# 强制续期
certbot renew --force-renewal
systemctl reload nginx
```

### Nginx 报错

```bash
# 测试配置语法
nginx -t

# 查看错误日志
tail -f /var/log/nginx/error.log
```

## 🛡️ 安全配置说明

Nginx 配置已包含以下安全措施：

- **TLS 1.2/1.3** - 禁用旧版不安全协议
- **现代加密套件** - 使用 ECDHE + AES-GCM / ChaCha20
- **HSTS** - 强制浏览器使用 HTTPS
- **HTTP/2** - 更快的传输协议
- **Session 复用** - 提高性能

## 📊 SSL 评级测试

配置完成后，可以测试 SSL 安全等级：

- [SSL Labs](https://www.ssllabs.com/ssltest/analyze.html?d=canway.site)
- [Security Headers](https://securityheaders.com/?q=canway.site)

目标：达到 **A+** 评级 ✨
