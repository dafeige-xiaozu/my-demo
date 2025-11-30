# 多用户待办事项 API 使用指南

## 🎯 概述

这是一个基于 FastAPI + SQLAlchemy + JWT 认证的多用户待办事项管理系统。支持用户注册、登录和任务管理，包括截止日期功能。

## 📚 API 端点

### 认证相关

#### 1. 用户注册
- **端点**: `POST /api/users`
- **描述**: 创建新用户账户
- **请求体**:
```json
{
  "username": "john_doe",
  "password": "your_secure_password"
}
```
- **响应**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "john_doe",
    "created_at": "2025-01-01T12:00:00"
  },
  "message": "用户注册成功"
}
```

#### 2. 用户登录
- **端点**: `POST /api/token`
- **描述**: 验证用户凭证并获取 JWT Token
- **请求体**:
```json
{
  "username": "john_doe",
  "password": "your_secure_password"
}
```
- **响应**:
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  },
  "message": "登录成功"
}
```

### 待办事项相关

> **注意**: 所有 Todo 端点都需要在请求头中提供 JWT Token

#### 3. 获取用户的所有待办事项
- **端点**: `GET /api/todos`
- **认证**: 需要 Bearer Token
- **请求头**:
```
Authorization: Bearer <your_access_token>
```
- **响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "text": "完成项目文档",
      "completed": false,
      "due_date": "2025-01-15",
      "created_at": "2025-01-01T12:00:00",
      "updated_at": "2025-01-01T12:00:00"
    }
  ],
  "message": "获取待办事项成功"
}
```

#### 4. 创建待办事项
- **端点**: `POST /api/todos`
- **认证**: 需要 Bearer Token
- **请求体**:
```json
{
  "text": "完成项目文档",
  "completed": false,
  "due_date": "2025-01-15"
}
```
- **响应**: 返回创建的待办事项信息

#### 5. 更新待办事项
- **端点**: `PUT /api/todos/{todo_id}`
- **认证**: 需要 Bearer Token
- **请求体** (所有字段可选):
```json
{
  "text": "修改后的任务文本",
  "completed": true,
  "due_date": "2025-01-20"
}
```
- **响应**: 返回更新后的待办事项信息

#### 6. 删除待办事项
- **端点**: `DELETE /api/todos/{todo_id}`
- **认证**: 需要 Bearer Token
- **响应**:
```json
{
  "success": true,
  "data": {
    "id": 1
  },
  "message": "删除待办事项成功"
}
```

## 🔐 认证说明

### JWT Token 使用

1. **获取 Token**: 通过 `/api/token` 端点登录获取
2. **使用 Token**: 在请求头中添加 `Authorization: Bearer <token>`
3. **Token 有效期**: 默认 30 分钟
4. **刷新机制**: Token 过期后需要重新登录

### 安全特性

- ✅ 密码使用 bcrypt 加密存储
- ✅ JWT Token 有时间限制
- ✅ 用户数据隔离（只能访问自己的任务）
- ✅ 操作权限检查（无法修改或删除他人的任务）

## 🧪 测试示例

### 使用 cURL

```bash
# 1. 注册用户
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "test123456"
  }'

# 2. 登录
curl -X POST http://localhost:8000/api/token \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_user",
    "password": "test123456"
  }'

# 3. 获取 Token (从上面响应中复制)
TOKEN="your_access_token_here"

# 4. 创建待办事项
curl -X POST http://localhost:8000/api/todos \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "text": "学习 FastAPI",
    "due_date": "2025-01-20"
  }'

# 5. 获取所有待办事项
curl -X GET http://localhost:8000/api/todos \
  -H "Authorization: Bearer $TOKEN"

# 6. 更新待办事项
curl -X PUT http://localhost:8000/api/todos/1 \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "completed": true
  }'

# 7. 删除待办事项
curl -X DELETE http://localhost:8000/api/todos/1 \
  -H "Authorization: Bearer $TOKEN"
```

### 使用 Postman

1. **创建环境变量**:
   - `base_url`: `http://localhost:8000`
   - `token`: (登录后自动设置)

2. **注册用户**: 
   - Method: POST
   - URL: `{{base_url}}/api/users`
   - Body (raw JSON): 用户数据

3. **登录**:
   - Method: POST
   - URL: `{{base_url}}/api/token`
   - 将响应的 `access_token` 保存到环境变量 `token`

4. **使用 Token**:
   - 所有 Todo 请求都在 Headers 中添加:
   - Key: `Authorization`
   - Value: `Bearer {{token}}`

## 📊 数据库结构

### Users 表
```
id (主键)
username (唯一索引)
hashed_password
created_at
```

### Todos 表
```
id (主键)
user_id (外键关联 Users)
text
completed (布尔值，默认 False)
due_date (可选日期字段)
created_at
updated_at
```

## ⚠️ 常见错误

| 错误代码 | 错误消息 | 解决方案 |
|---------|--------|--------|
| 400 | 用户名已存在 | 更换用户名重新注册 |
| 401 | 用户名或密码错误 | 检查用户名和密码是否正确 |
| 401 | 无效的 Token | Token 已过期，需要重新登录 |
| 403 | 无权修改此待办事项 | 无法修改他人的任务 |
| 404 | 待办事项不存在 | 检查任务 ID 是否正确 |

## 🚀 部署注意事项

### 生产环境

1. **更改 SECRET_KEY**:
   - 编辑 `backend/security.py`
   - 将 `SECRET_KEY` 改为强密码字符串或从环境变量读取

2. **配置 CORS**:
   - 修改 `main.py` 中的 `allow_origins`
   - 改为具体的前端域名而不是 `["*"]`

3. **使用环境变量**:
   - 将敏感信息如 SECRET_KEY 存储在 `.env` 文件
   - 使用 `python-dotenv` 加载

### 本地开发

```bash
# 安装依赖
pip install -r requirements.txt

# 运行服务
python -m uvicorn backend.main:app --reload

# 访问 API 文档
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

## 📝 版本更新

### v2.0.0 (当前版本)
- ✅ 实现多用户系统
- ✅ JWT 认证
- ✅ 任务截止日期
- ✅ 用户数据隔离
- ✅ 操作权限检查

### v1.0.0
- ✅ 基础 Todo CRUD 功能
- ✅ SQLAlchemy ORM
- ✅ FastAPI 框架

## 📞 联系方式

如有问题或建议，请提交 Issue 或 PR。
