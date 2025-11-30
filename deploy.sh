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

# 步骤3：安装后端依赖
echo -e "${YELLOW}[3/4] 安装后端依赖...${NC}"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'EOF'
  cd /root/todo-app/server
  npm install --production
EOF

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ 后端依赖安装成功${NC}"
else
  echo -e "${RED}❌ 后端依赖安装失败${NC}"
  exit 1
fi

# 步骤4：启动应用（使用 PM2 或 nohup）
echo -e "${YELLOW}[4/4] 启动应用...${NC}"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'EOF'
  cd /root/todo-app/server
  
  # 如果已安装 PM2，使用 PM2 启动
  if command -v pm2 &> /dev/null; then
    pm2 delete todo-server 2>/dev/null || true
    pm2 start index.js --name "todo-server" --env production
    pm2 save
    echo "✅ 使用 PM2 启动服务"
  else
    # 否则使用 nohup 启动
    nohup npm start > /root/todo-app/server.log 2>&1 &
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
echo -e "服务器地址: http://182.92.82.185:3001/api/todos"
echo -e "前端地址: http://182.92.82.185:5173 (如果配置了 nginx)"
