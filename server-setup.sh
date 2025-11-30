#!/bin/bash

# 阿里云服务器初始化脚本
# 用法: bash server-setup.sh

SSH_KEY="$HOME/Desktop/MyMac.pem"
SERVER_USER="root"
SERVER_IP="182.92.82.185"

echo "================================"
echo "开始初始化阿里云服务器环境..."
echo "================================"

# 连接到服务器并执行初始化
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'EOF'

echo "================================"
echo "开始服务器环境配置..."
echo "================================"

# 更新系统包
echo "[1/6] 更新系统包..."
apt-get update
apt-get upgrade -y

# 安装必要的工具
echo "[2/6] 安装必要工具..."
apt-get install -y curl wget git build-essential python3

# 安装 Node.js 和 npm
echo "[3/6] 安装 Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# 验证安装
echo "[4/6] 验证安装..."
node --version
npm --version

# 安装 PM2 进程管理器
echo "[5/6] 安装 PM2..."
npm install -g pm2

# 创建应用目录
echo "[6/6] 创建应用目录..."
mkdir -p /root/todo-app

echo "================================"
echo "✅ 服务器环境初始化完成！"
echo "================================"
echo "接下来运行: npm run deploy"

EOF
