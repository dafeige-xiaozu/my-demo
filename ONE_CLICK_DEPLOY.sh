#!/bin/bash
# 一键部署脚本 - 在阿里云服务器上直接执行
# bash ONE_CLICK_DEPLOY.sh

set -e

echo "=================================================="
echo "🚀 Todo App 一键部署脚本"
echo "=================================================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 步骤 1: 更新系统
echo -e "${YELLOW}[1/12] 更新系统...${NC}"
apt-get update -qq
apt-get upgrade -y -qq

# 步骤 2: 安装基础工具
echo -e "${YELLOW}[2/12] 安装基础工具...${NC}"
apt-get install -y curl wget git build-essential python3 python3-pip nodejs npm nginx -qq

# 步骤 3: 升级 Node.js
echo -e "${YELLOW}[3/12] 升级 Node.js...${NC}"
curl -fsSL https://deb.nodesource.com/setup_18.x | bash - -qq
apt-get install -y nodejs -qq

# 步骤 4: 安装 PM2
echo -e "${YELLOW}[4/12] 安装 PM2...${NC}"
npm install -g pm2 -q

# 步骤 5: 克隆项目
echo -e "${YELLOW}[5/12] 克隆项目代码...${NC}"
cd /root
if [ -d "my-demo" ]; then
  cd my-demo
  git pull origin main
else
  git clone https://github.com/dafeige-xiaozu/my-demo.git
  cd my-demo
fi

# 步骤 6: 安装前端依赖
echo -e "${YELLOW}[6/12] 安装前端依赖...${NC}"
npm install -q
npm run build -q

# 步骤 7: 安装 Python 依赖
echo -e "${YELLOW}[7/12] 安装 Python 依赖...${NC}"
pip install -r requirements.txt -q

# 步骤 8: 启动后端服务
echo -e "${YELLOW}[8/12] 启动 FastAPI 后端...${NC}"
pm2 delete todo-backend 2>/dev/null || true
pm2 start "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000" --name "todo-backend"
pm2 save

# 步骤 9: 启动前端服务
echo -e "${YELLOW}[9/12] 启动前端服务...${NC}"
pm2 delete todo-frontend 2>/dev/null || true
pm2 start "python -m http.server 5173 --directory /root/my-demo/dist" --name "todo-frontend"

# 步骤 10: 配置 Nginx
echo -e "${YELLOW}[10/12] 配置 Nginx...${NC}"
cat > /etc/nginx/sites-available/todo-app << 'EOF'
upstream backend {
    server localhost:8000;
}

server {
    listen 80;
    server_name 182.92.82.185;
    client_max_body_size 100M;
    
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
    
    location /openapi.json {
        proxy_pass http://backend/openapi.json;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
    }
}
EOF

ln -sf /etc/nginx/sites-available/todo-app /etc/nginx/sites-enabled/todo-app
rm -f /etc/nginx/sites-enabled/default

# 步骤 11: 启动 Nginx
echo -e "${YELLOW}[11/12] 启动 Nginx...${NC}"
nginx -t 2>/dev/null
systemctl restart nginx
systemctl enable nginx

# 步骤 12: 验证部署
echo -e "${YELLOW}[12/12] 验证部署...${NC}"
sleep 2

echo ""
echo -e "${GREEN}=================================================="
echo "✅ 部署完成！"
echo "==================================================${NC}"
echo ""
echo "📍 访问地址："
echo "  🌐 前端应用: http://182.92.82.185"
echo "  📚 API 文档: http://182.92.82.185/docs"
echo "  🔗 API 地址: http://182.92.82.185/api/todos"
echo "  📖 ReDoc: http://182.92.82.185/redoc"
echo ""
echo "🔧 服务管理："
echo "  查看进程: pm2 list"
echo "  查看日志: pm2 logs todo-backend"
echo "  重启服务: pm2 restart todo-backend"
echo "  Nginx 状态: systemctl status nginx"
echo ""
echo -e "${GREEN}=================================================="
echo "🎉 应用已成功部署到阿里云！"
echo "==================================================${NC}"
