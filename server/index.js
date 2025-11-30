const express = require('express')
const cors = require('cors')
const {
  getAllTodos,
  getTodoById,
  addTodo,
  updateTodo,
  deleteTodo,
} = require('./db')

const app = express()
const PORT = process.env.PORT || 3001

// 中间件
app.use(cors())
app.use(express.json())

// 日志中间件
app.use((req, res, next) => {
  console.log(`${req.method} ${req.path}`)
  next()
})

// ==================== API 路由 ====================

// GET /api/todos - 获取所有待办事项
app.get('/api/todos', (req, res) => {
  try {
    const todos = getAllTodos()
    // 将 SQLite 的 0/1 转换为布尔值
    const formattedTodos = todos.map(todo => ({
      ...todo,
      completed: Boolean(todo.completed),
    }))
    res.json({
      success: true,
      data: formattedTodos,
    })
  } catch (error) {
    console.error('Error fetching todos:', error)
    res.status(500).json({
      success: false,
      message: 'Failed to fetch todos',
      error: error.message,
    })
  }
})

// POST /api/todos - 创建新的待办事项
app.post('/api/todos', (req, res) => {
  try {
    const { text } = req.body
    if (!text || typeof text !== 'string' || text.trim() === '') {
      return res.status(400).json({
        success: false,
        message: 'Text is required and must be non-empty',
      })
    }
    const todo = addTodo(text.trim())
    res.status(201).json({
      success: true,
      data: {
        ...todo,
        completed: Boolean(todo.completed),
      },
    })
  } catch (error) {
    console.error('Error creating todo:', error)
    res.status(500).json({
      success: false,
      message: 'Failed to create todo',
      error: error.message,
    })
  }
})

// PUT /api/todos/:id - 更新待办事项
app.put('/api/todos/:id', (req, res) => {
  try {
    const { id } = req.params
    const { text, completed } = req.body

    const todo = getTodoById(id)
    if (!todo) {
      return res.status(404).json({
        success: false,
        message: 'Todo not found',
      })
    }

    // 使用提供的值或保留原有值
    const updateData = {
      text: text !== undefined ? text : todo.text,
      completed: completed !== undefined ? completed : Boolean(todo.completed),
    }

    const updatedTodo = updateTodo(id, updateData)
    res.json({
      success: true,
      data: {
        ...updatedTodo,
        completed: Boolean(updatedTodo.completed),
      },
    })
  } catch (error) {
    console.error('Error updating todo:', error)
    res.status(500).json({
      success: false,
      message: 'Failed to update todo',
      error: error.message,
    })
  }
})

// DELETE /api/todos/:id - 删除待办事项
app.delete('/api/todos/:id', (req, res) => {
  try {
    const { id } = req.params

    const todo = getTodoById(id)
    if (!todo) {
      return res.status(404).json({
        success: false,
        message: 'Todo not found',
      })
    }

    deleteTodo(id)
    res.json({
      success: true,
      message: 'Todo deleted successfully',
      id: parseInt(id),
    })
  } catch (error) {
    console.error('Error deleting todo:', error)
    res.status(500).json({
      success: false,
      message: 'Failed to delete todo',
      error: error.message,
    })
  }
})

// ==================== 错误处理 ====================

// 404 处理
app.use((req, res) => {
  res.status(404).json({
    success: false,
    message: 'Not found',
  })
})

// 全局错误处理
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err)
  res.status(500).json({
    success: false,
    message: 'Internal server error',
    error: err.message,
  })
})

// 启动服务器
app.listen(PORT, () => {
  console.log(`✅ Todo API Server running on http://localhost:${PORT}`)
  console.log(`📚 API Documentation:`)
  console.log(`   GET    http://localhost:${PORT}/api/todos`)
  console.log(`   POST   http://localhost:${PORT}/api/todos`)
  console.log(`   PUT    http://localhost:${PORT}/api/todos/:id`)
  console.log(`   DELETE http://localhost:${PORT}/api/todos/:id`)
})
