#!/bin/bash

# 阿里云 Nginx 配置脚本
# 用途：在阿里云服务器上配置 Nginx 作为反向代理

SSH_KEY="$HOME/Desktop/MyMac.pem"
SERVER_USER="root"
SERVER_IP="182.92.82.185"

echo "================================"
echo "开始配置 Nginx 反向代理..."
echo "================================"

ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'EOF'

echo "[1/3] 安装 Nginx..."
apt-get update -qq
apt-get install -y nginx

echo "[2/3] 配置 Nginx..."

# 创建 Nginx 配置文件
cat > /etc/nginx/sites-available/todo-app << 'NGINX_CONFIG'
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:5173;
}

server {
    listen 80;
    server_name 182.92.82.185;
    
    # 前端静态资源
    location / {
        root /root/todo-app/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # 后端 API 代理
    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # FastAPI 特定配置
        proxy_read_timeout 30s;
        proxy_connect_timeout 30s;
    }
    
    # API 文档
    location /docs {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
    
    location /redoc {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
    
    location /openapi.json {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
NGINX_CONFIG

# 启用配置
ln -sf /etc/nginx/sites-available/todo-app /etc/nginx/sites-enabled/todo-app
rm -f /etc/nginx/sites-enabled/default

# 测试 Nginx 配置
echo "[3/3] 测试和启动 Nginx..."
nginx -t

if [ $? -eq 0 ]; then
    systemctl restart nginx
    systemctl enable nginx
    echo "✅ Nginx 配置成功！"
    echo ""
    echo "访问地址："
    echo "  前端: http://182.92.82.185"
    echo "  API: http://182.92.82.185/api/todos"
    echo "  文档: http://182.92.82.185/docs"
else
    echo "❌ Nginx 配置失败，请检查配置文件"
    exit 1
fi

EOF

echo ""
echo "================================"
echo "✅ Nginx 配置完成！"
echo "================================"
echo ""
echo "访问地址："
echo "  前端: http://182.92.82.185"
echo "  API: http://182.92.82.185/api/todos"
echo "  文档: http://182.92.82.185/docs"
echo ""
echo "如果需要 HTTPS，需要配置 SSL 证书（使用 Let's Encrypt）"
echo "运行: bash aliyun-ssl-setup.sh"
