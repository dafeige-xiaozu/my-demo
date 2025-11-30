#!/bin/bash

# 配置变量
SERVER_IP="182.92.82.185"
SERVER_USER="root"
SSH_KEY="$HOME/Desktop/MyMac.pem"
APP_DIR="/root/todo-app"
GITHUB_REPO="https://github.com/dafeige-xiaozu/my-demo.git"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}开始部署到阿里云服务器...${NC}"

# 步骤1：连接到服务器并克隆/更新代码
echo -e "${YELLOW}[1/4] 连接到服务器并检查代码...${NC}"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'EOF'
  if [ -d /root/todo-app ]; then
    echo "更新现有代码..."
    cd /root/todo-app
    git pull origin main
  else
    echo "克隆新代码..."
    git clone https://github.com/dafeige-xiaozu/my-demo.git /root/todo-app
    cd /root/todo-app
  fi
EOF

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ 代码更新成功${NC}"
else
  echo -e "${RED}❌ 代码更新失败${NC}"
  exit 1
fi

# 步骤2：安装前端依赖并构建
echo -e "${YELLOW}[2/4] 构建前端应用...${NC}"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'EOF'
  cd /root/todo-app
  npm install
  npm run build
EOF

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ 前端构建成功${NC}"
else
  echo -e "${RED}❌ 前端构建失败${NC}"
  exit 1
fi

# 步骤3：安装 Python 依赖
echo -e "${YELLOW}[3/5] 安装 Python 依赖...${NC}"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'EOF'
  cd /root/todo-app
  pip install -r requirements.txt -q
EOF

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Python 依赖安装成功${NC}"
else
  echo -e "${RED}❌ Python 依赖安装失败${NC}"
  exit 1
fi

# 步骤4：配置前端代理
echo -e "${YELLOW}[4/5] 配置 Nginx 反向代理...${NC}"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'EOF'
  # 不在这里配置 nginx，需要手动配置
echo "✅ 需要手动配置 Nginx。代理设置子第二步。"
EOF

# 步骤5：启动应用（使用 PM2 或 nohup）
echo -e "${YELLOW}[5/5] 启动应用...${NC}"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'EOF'
  cd /root/todo-app
  
  # 如果已安装 PM2，使用 PM2 启动
  if command -v pm2 &> /dev/null; then
    pm2 delete todo-backend 2>/dev/null || true
    pm2 start "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000" --name "todo-backend" --env production
    pm2 delete todo-frontend 2>/dev/null || true
    pm2 serve dist 5173 --name "todo-frontend" --spa 2>/dev/null || true
    pm2 save
    echo "✅ 使用 PM2 启动服务"
  else
    # 否则使用 nohup 启动
    nohup python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 > /root/todo-app/backend.log 2>&1 &
    nohup python -m http.server 5173 --directory /root/todo-app/dist > /root/todo-app/frontend.log 2>&1 &
    echo "✅ 使用 nohup 启动服务"
  fi
EOF

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ 应用启动成功${NC}"
else
  echo -e "${RED}❌ 应用启动失败${NC}"
  exit 1
fi

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}✅ 部署完成！${NC}"
echo -e "${GREEN}================================${NC}"
echo -e "后端地址: http://182.92.82.185:8000"
echo -e "后端 API: http://182.92.82.185:8000/api/todos"
echo -e "前端地址: http://182.92.82.185:5173 (需要 nginx 配置)"
echo -e "配置 npm 脚本: npm run deploy"
echo -e "\n接下来需要手动配置 Nginx。运行 bash aliyun-nginx-setup.sh"
