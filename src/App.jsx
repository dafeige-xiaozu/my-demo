import { useState, useEffect } from 'react'

const API_BASE_URL = '/api'

function App() {
  const [todos, setTodos] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [filter, setFilter] = useState('all') // 'all' | 'active' | 'completed'
  const [editingId, setEditingId] = useState(null)
  const [editingText, setEditingText] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // 初始化时从服务器获取数据
  useEffect(() => {
    fetchTodos()
  }, [])

  // 从服务器获取所有待办事项
  const fetchTodos = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await fetch(`${API_BASE_URL}/todos`)
      if (!response.ok) throw new Error('Failed to fetch todos')
      const result = await response.json()
      setTodos(result.data || [])
    } catch (err) {
      console.error('Error fetching todos:', err)
      setError('无法加载待办事项')
      setTodos([])
    } finally {
      setLoading(false)
    }
  }

  // 添加任务
  const addTodo = async () => {
    if (inputValue.trim() === '') return
    
    try {
      const response = await fetch(`${API_BASE_URL}/todos`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: inputValue }),
      })
      if (!response.ok) throw new Error('Failed to add todo')
      const result = await response.json()
      setTodos([result.data, ...todos])
      setInputValue('')
    } catch (err) {
      console.error('Error adding todo:', err)
      setError('添加任务失败')
    }
  }

  // 删除任务
  const deleteTodo = async (id) => {
    try {
      const response = await fetch(`${API_BASE_URL}/todos/${id}`, {
        method: 'DELETE',
      })
      if (!response.ok) throw new Error('Failed to delete todo')
      setTodos(todos.filter(todo => todo.id !== id))
    } catch (err) {
      console.error('Error deleting todo:', err)
      setError('删除任务失败')
    }
  }

  // 切换完成状态
  const toggleComplete = async (id) => {
    const todo = todos.find(t => t.id === id)
    if (!todo) return
    
    try {
      const response = await fetch(`${API_BASE_URL}/todos/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed: !todo.completed }),
      })
      if (!response.ok) throw new Error('Failed to update todo')
      const result = await response.json()
      setTodos(todos.map(t => t.id === id ? result.data : t))
    } catch (err) {
      console.error('Error updating todo:', err)
      setError('更新任务失败')
    }
  }

  // 开始编辑
  const startEdit = (id, text) => {
    setEditingId(id)
    setEditingText(text)
  }

  // 保存编辑
  const saveEdit = async (id) => {
    if (editingText.trim() === '') {
      setEditingId(null)
      return
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/todos/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: editingText }),
      })
      if (!response.ok) throw new Error('Failed to update todo')
      const result = await response.json()
      setTodos(todos.map(t => t.id === id ? result.data : t))
      setEditingId(null)
      setEditingText('')
    } catch (err) {
      console.error('Error updating todo:', err)
      setError('编辑任务失败')
    }
  }

  // 取消编辑
  const cancelEdit = () => {
    setEditingId(null)
    setEditingText('')
  }

  // 过滤任务
  const filteredTodos = todos.filter(todo => {
    if (filter === 'active') return !todo.completed
    if (filter === 'completed') return todo.completed
    return true
  })

  // 计算未完成任务数
  const activeCount = todos.filter(todo => !todo.completed).length

  // 按下回车键添加任务
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      addTodo()
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-400 via-pink-500 to-red-500 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* 标题 */}
        <h1 className="text-5xl font-bold text-white text-center mb-8 drop-shadow-lg">
          ✨ 我的待办事项
        </h1>

        {/* 错误提示 */}
        {error && (
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6 rounded-lg">
            <p className="font-semibold">⚠️ 错误</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* 加载则 */}
        {loading ? (
          <div className="bg-white rounded-2xl shadow-2xl p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
            <p className="text-gray-600 mt-4">正在加载丫务...</p>
          </div>
        ) : (
          <>
            {/* 输入区域 */}
            <div className="bg-white rounded-2xl shadow-2xl p-6 mb-6">
              <div className="flex gap-3">
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="输入新任务..."
                  className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-purple-500 transition-colors text-gray-700 placeholder-gray-400"
                />
                <button
                  onClick={addTodo}
                  className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all transform hover:scale-105 active:scale-95 shadow-lg"
                >
                  添加
                </button>
              </div>
            </div>

            {/* 过滤按钮 */}
            {todos.length > 0 && (
              <div className="flex gap-3 justify-center mb-6">
                <button
                  onClick={() => setFilter('all')}
                  className={`px-5 py-2 rounded-lg font-medium transition-all transform hover:scale-105 ${
                    filter === 'all'
                      ? 'bg-white text-purple-600 shadow-lg'
                      : 'bg-white/80 text-gray-600 hover:bg-white'
                  }`}
                >
                  全部 ({todos.length})
                </button>
                <button
                  onClick={() => setFilter('active')}
                  className={`px-5 py-2 rounded-lg font-medium transition-all transform hover:scale-105 ${
                    filter === 'active'
                      ? 'bg-white text-purple-600 shadow-lg'
                      : 'bg-white/80 text-gray-600 hover:bg-white'
                  }`}
                >
                  进行中 ({activeCount})
                </button>
                <button
                  onClick={() => setFilter('completed')}
                  className={`px-5 py-2 rounded-lg font-medium transition-all transform hover:scale-105 ${
                    filter === 'completed'
                      ? 'bg-white text-purple-600 shadow-lg'
                      : 'bg-white/80 text-gray-600 hover:bg-white'
                  }`}
                >
                  已完成 ({todos.length - activeCount})
                </button>
              </div>
            )}

            {/* 任务列表 */}
            <div className="bg-white rounded-2xl shadow-2xl p-6">
              {filteredTodos.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-gray-400 text-lg">
                    {todos.length === 0 ? '暂无任务，开始添加吧！ 🎯' : '没有符合条件的任务 📭'}
                  </p>
                </div>
              ) : (
                <ul className="space-y-3">
                  {filteredTodos.map((todo) => (
                    <li
                      key={todo.id}
                      className="flex items-center gap-3 bg-gradient-to-r from-gray-50 to-gray-100 p-4 rounded-lg hover:from-purple-50 hover:to-pink-50 transition-all group"
                    >
                      {/* 复选框 */}
                      <input
                        type="checkbox"
                        checked={todo.completed}
                        onChange={() => toggleComplete(todo.id)}
                        className="w-5 h-5 rounded border-2 border-gray-300 text-purple-600 focus:ring-2 focus:ring-purple-500 cursor-pointer"
                      />

                      {/* 任务内容或编辑输入框 */}
                      {editingId === todo.id ? (
                        <div className="flex-1 flex gap-2">
                          <input
                            type="text"
                            value={editingText}
                            onChange={(e) => setEditingText(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && saveEdit(todo.id)}
                            className="flex-1 px-3 py-2 border-2 border-purple-400 rounded-lg focus:outline-none focus:border-purple-600 text-gray-700"
                            autoFocus
                          />
                          <button
                            onClick={() => saveEdit(todo.id)}
                            className="px-4 py-2 bg-green-500 text-white font-medium rounded-lg hover:bg-green-600 transition-all transform hover:scale-105 active:scale-95 shadow-md"
                          >
                            保存
                          </button>
                          <button
                            onClick={cancelEdit}
                            className="px-4 py-2 bg-gray-500 text-white font-medium rounded-lg hover:bg-gray-600 transition-all transform hover:scale-105 active:scale-95 shadow-md"
                          >
                            取消
                          </button>
                        </div>
                      ) : (
                        <>
                          <span
                            onClick={() => startEdit(todo.id, todo.text)}
                            className={`flex-1 text-lg cursor-pointer ${
                              todo.completed
                                ? 'line-through text-gray-400'
                                : 'text-gray-700'
                            }`}
                          >
                            {todo.text}
                          </span>
                          <button
                            onClick={() => deleteTodo(todo.id)}
                            className="px-4 py-2 bg-red-500 text-white font-medium rounded-lg hover:bg-red-600 transition-all transform hover:scale-105 active:scale-95 shadow-md opacity-90 group-hover:opacity-100"
                          >
                            删除
                          </button>
                        </>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>

            {/* 统计信息 */}
            {todos.length > 0 && (
              <div className="mt-6 text-center text-white text-lg font-semibold drop-shadow">
                剩余 {activeCount} 个未完成任务 · 共 {todos.length} 个任务
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}

export default App
