#!/bin/bash
# 阿里云服务器部署命令清单
# 直接在服务器上执行这些命令

echo "=========================================="
echo "Todo App - 阿里云部署步骤"
echo "=========================================="

# 步骤 1: 初始化系统环境
echo ""
echo "[步骤 1] 初始化系统环境..."
echo "执行命令："
echo "apt-get update && apt-get upgrade -y"
echo "apt-get install -y curl wget git build-essential python3 python3-pip nodejs npm"
echo ""

# 步骤 2: 安装 Node.js 和 npm
echo "[步骤 2] 安装 Node.js 18+"
echo "执行命令："
echo "curl -fsSL https://deb.nodesource.com/setup_18.x | bash -"
echo "apt-get install -y nodejs"
echo "node --version && npm --version"
echo ""

# 步骤 3: 安装 PM2
echo "[步骤 3] 安装 PM2 进程管理器"
echo "执行命令："
echo "npm install -g pm2"
echo ""

# 步骤 4: 克隆项目
echo "[步骤 4] 克隆项目代码"
echo "执行命令："
echo "cd /root"
echo "git clone https://github.com/dafeige-xiaozu/my-demo.git"
echo "cd /root/my-demo"
echo ""

# 步骤 5: 安装前端依赖
echo "[步骤 5] 安装前端依赖并构建"
echo "执行命令："
echo "cd /root/my-demo"
echo "npm install"
echo "npm run build"
echo ""

# 步骤 6: 安装 Python 依赖
echo "[步骤 6] 安装 Python 依赖"
echo "执行命令："
echo "cd /root/my-demo"
echo "pip install -r requirements.txt"
echo ""

# 步骤 7: 启动后端服务
echo "[步骤 7] 启动 FastAPI 后端服务"
echo "执行命令："
echo "cd /root/my-demo"
echo "pm2 start 'python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000' --name 'todo-backend' --env production"
echo "pm2 save"
echo ""

# 步骤 8: 启动前端静态服务
echo "[步骤 8] 启动前端静态服务"
echo "执行命令："
echo "pm2 start 'python -m http.server 5173 --directory /root/my-demo/dist' --name 'todo-frontend'"
echo "pm2 save"
echo ""

# 步骤 9: 安装 Nginx
echo "[步骤 9] 安装 Nginx"
echo "执行命令："
echo "apt-get install -y nginx"
echo ""

# 步骤 10: 配置 Nginx
echo "[步骤 10] 配置 Nginx 反向代理"
echo "创建 /etc/nginx/sites-available/todo-app 文件，内容如下："
echo ""
echo "======== 开始复制以下内容 ========"
echo ""
cat << 'NGINX_CONFIG'
upstream backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name 182.92.82.185;
    
    # 前端静态资源
    location / {
        root /root/my-demo/dist;
        try_files $uri $uri/ /index.html;
    }
    
    # 后端 API 代理
    location /api/ {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 30s;
        proxy_connect_timeout 30s;
    }
    
    # API 文档
    location /docs {
        proxy_pass http://backend/docs;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
    
    location /redoc {
        proxy_pass http://backend/redoc;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
NGINX_CONFIG
echo ""
echo "======== 结束复制 ========"
echo ""

# 步骤 11: 启用 Nginx 配置
echo "[步骤 11] 启用 Nginx 配置"
echo "执行命令："
echo "ln -sf /etc/nginx/sites-available/todo-app /etc/nginx/sites-enabled/todo-app"
echo "rm -f /etc/nginx/sites-enabled/default"
echo "nginx -t"
echo "systemctl restart nginx"
echo "systemctl enable nginx"
echo ""

# 步骤 12: 验证部署
echo "[步骤 12] 验证部署"
echo "执行命令："
echo "pm2 list"
echo "systemctl status nginx"
echo ""

echo "=========================================="
echo "部署完成！"
echo "=========================================="
echo ""
echo "访问地址："
echo "  前端应用: http://182.92.82.185"
echo "  API 文档: http://182.92.82.185/docs"
echo "  API 地址: http://182.92.82.185/api/todos"
echo ""
