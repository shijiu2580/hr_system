#!/bin/bash
# SSL 证书申请/续期脚本
# 使用 Let's Encrypt 免费证书 + Certbot

set -e

DOMAIN="canway.site"
EMAIL="483496381@qq.com"

echo "========================================="
echo "  canway.site SSL 证书配置脚本"
echo "========================================="

# 检查是否为 root
if [ "$EUID" -ne 0 ]; then
    echo "请使用 root 权限运行此脚本"
    echo "sudo $0"
    exit 1
fi

# 安装 Certbot
install_certbot() {
    echo ""
    echo ">>> 安装 Certbot..."
    
    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        apt-get update
        apt-get install -y certbot python3-certbot-nginx
    elif command -v yum &> /dev/null; then
        # CentOS/RHEL
        yum install -y epel-release
        yum install -y certbot python3-certbot-nginx
    else
        echo "不支持的系统，请手动安装 certbot"
        exit 1
    fi
    
    echo "✓ Certbot 安装完成"
}

# 申请证书
request_cert() {
    echo ""
    echo ">>> 申请 SSL 证书..."
    echo "域名: $DOMAIN, www.$DOMAIN, m.$DOMAIN, api.$DOMAIN"
    
    # 使用 webroot 模式或 nginx 模式申请
    certbot certonly \
        --nginx \
        -d $DOMAIN \
        -d www.$DOMAIN \
        -d m.$DOMAIN \
        -d api.$DOMAIN \
        --email $EMAIL \
        --agree-tos \
        --non-interactive \
        --expand
    
    echo "✓ 证书申请成功"
    echo ""
    echo "证书位置:"
    echo "  证书: /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
    echo "  私钥: /etc/letsencrypt/live/$DOMAIN/privkey.pem"
}

# 配置自动续期
setup_auto_renew() {
    echo ""
    echo ">>> 配置自动续期..."
    
    # 创建续期钩子脚本
    cat > /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh << 'EOF'
#!/bin/bash
systemctl reload nginx
EOF
    chmod +x /etc/letsencrypt/renewal-hooks/deploy/reload-nginx.sh
    
    # 添加 cron 定时任务 (每天凌晨3点检查)
    (crontab -l 2>/dev/null | grep -v certbot; echo "0 3 * * * certbot renew --quiet") | crontab -
    
    echo "✓ 自动续期已配置 (每天 3:00 检查)"
}

# 启用 Nginx HTTPS 配置
enable_https() {
    echo ""
    echo ">>> 启用 HTTPS 配置..."
    
    NGINX_CONF="/etc/nginx/sites-available/canway.site.conf"
    
    if [ -f "$NGINX_CONF" ]; then
        # 备份原配置
        cp $NGINX_CONF ${NGINX_CONF}.bak
        
        # 替换配置 - 取消 SSL 相关注释
        sed -i 's/# listen 443 ssl http2;/listen 443 ssl http2;/g' $NGINX_CONF
        sed -i 's/# ssl_certificate /ssl_certificate /g' $NGINX_CONF
        sed -i 's/# ssl_certificate_key /ssl_certificate_key /g' $NGINX_CONF
        sed -i 's/# ssl_protocols /ssl_protocols /g' $NGINX_CONF
        sed -i 's/# ssl_ciphers /ssl_ciphers /g' $NGINX_CONF
        sed -i 's/# ssl_prefer_server_ciphers /ssl_prefer_server_ciphers /g' $NGINX_CONF
        
        # 启用 HTTP -> HTTPS 重定向
        # 这部分需要手动启用，因为多行注释处理复杂
        
        echo "✓ HTTPS 配置已启用"
        echo ""
        echo "请手动编辑 $NGINX_CONF 启用 HTTP->HTTPS 重定向部分"
    else
        echo "! Nginx 配置文件不存在: $NGINX_CONF"
        echo "  请先将 canway.site.conf 复制到 /etc/nginx/sites-available/"
    fi
}

# 测试配置
test_config() {
    echo ""
    echo ">>> 测试 Nginx 配置..."
    nginx -t
    
    echo ""
    echo ">>> 重载 Nginx..."
    systemctl reload nginx
    
    echo "✓ Nginx 重载完成"
}

# 显示证书信息
show_cert_info() {
    echo ""
    echo "========================================="
    echo "  证书信息"
    echo "========================================="
    certbot certificates
}

# 主菜单
case "${1:-install}" in
    install|setup)
        install_certbot
        request_cert
        setup_auto_renew
        enable_https
        test_config
        show_cert_info
        echo ""
        echo "========================================="
        echo "  🎉 SSL 配置完成!"
        echo "========================================="
        echo ""
        echo "现在可以通过以下地址访问:"
        echo "  https://canway.site"
        echo "  https://m.canway.site"
        echo "  https://api.canway.site"
        ;;
    renew)
        echo ">>> 手动续期证书..."
        certbot renew --force-renewal
        systemctl reload nginx
        show_cert_info
        ;;
    status)
        show_cert_info
        ;;
    *)
        echo "用法: $0 {install|renew|status}"
        echo ""
        echo "  install  - 安装并申请证书 (首次使用)"
        echo "  renew    - 手动续期证书"
        echo "  status   - 查看证书状态"
        exit 1
        ;;
esac
