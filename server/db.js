const Database = require('better-sqlite3')
const path = require('path')

// 创建数据库连接
const dbPath = path.join(__dirname, 'todos.db')
const db = new Database(dbPath)

// 启用外键约束
db.pragma('foreign_keys = ON')

// 初始化数据库表
function initializeDatabase() {
  db.exec(`
    CREATE TABLE IF NOT EXISTS todos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      text TEXT NOT NULL,
      completed BOOLEAN DEFAULT 0,
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
  `)
}

// 获取所有 todos
function getAllTodos() {
  const stmt = db.prepare('SELECT * FROM todos ORDER BY id DESC')
  return stmt.all()
}

// 获取单个 todo
function getTodoById(id) {
  const stmt = db.prepare('SELECT * FROM todos WHERE id = ?')
  return stmt.get(id)
}

// 添加 todo
function addTodo(text) {
  const stmt = db.prepare('INSERT INTO todos (text, completed) VALUES (?, ?)')
  const result = stmt.run(text, 0)
  return getTodoById(result.lastInsertRowid)
}

// 更新 todo
function updateTodo(id, data) {
  const { text, completed } = data
  const stmt = db.prepare('UPDATE todos SET text = ?, completed = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?')
  stmt.run(text, completed ? 1 : 0, id)
  return getTodoById(id)
}

// 删除 todo
function deleteTodo(id) {
  const stmt = db.prepare('DELETE FROM todos WHERE id = ?')
  stmt.run(id)
  return { success: true, id }
}

// 初始化数据库
initializeDatabase()

module.exports = {
  db,
  getAllTodos,
  getTodoById,
  addTodo,
  updateTodo,
  deleteTodo,
}
