import { useState, useEffect } from 'react'

// API 基础地址，通过 Vite 代理到后端服务
const API_BASE_URL = '/api'

/**
 * 待办事项应用主组件
 * 
 * 功能说明：
 * - 从后端 API 获取和管理待办事项
 * - 支持添加、删除、编辑、完成状态切换
 * - 支持按状态过滤任务
 * - 实时同步数据到服务器
 */
function App() {
  // ==================== 状态管理 ====================
  
  /** 待办事项列表 */
  const [todos, setTodos] = useState([])
  
  /** 新任务输入框的值 */
  const [inputValue, setInputValue] = useState('')
  
  /** 任务过滤状态：'all' | 'active' | 'completed' */
  const [filter, setFilter] = useState('all')
  
  /** 当前正在编辑的任务 ID */
  const [editingId, setEditingId] = useState(null)
  
  /** 编辑中的任务文本内容 */
  const [editingText, setEditingText] = useState('')
  
  /** 数据加载状态 */
  const [loading, setLoading] = useState(true)
  
  /** 错误信息 */
  const [error, setError] = useState(null)

  // ==================== 生命周期钩子 ====================
  
  // 组件挂载时从服务器获取初始数据
  useEffect(() => {
    fetchTodos()
  }, [])

  // ==================== API 请求函数 ====================
  
  /**
   * 从服务器获取所有待办事项
   * 成功时更新 todos 状态，失败时显示错误信息
   */
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

  /**
   * 添加新任务
   * - 验证输入不为空
   * - 发送 POST 请求到后端
   * - 新任务插入到列表顶部
   */
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

  /**
   * 删除指定任务
   * @param {number} id - 待删除的任务 ID
   */
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

  /**
   * 切换任务的完成状态
   * @param {number} id - 待切换的任务 ID
   */
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

  /**
   * 进入编辑模式
   * @param {number} id - 待编辑的任务 ID
   * @param {string} text - 任务原文本
   */
  const startEdit = (id, text) => {
    setEditingId(id)
    setEditingText(text)
  }

  /**
   * 保存编辑内容
   * - 验证编辑文本不为空
   * - 发送 PUT 请求更新任务
   * - 更新本地状态
   * @param {number} id - 待更新的任务 ID
   */
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

  /**
   * 取消编辑，恢复正常显示
   */
  const cancelEdit = () => {
    setEditingId(null)
    setEditingText('')
  }

  // ==================== 数据处理 ====================
  
  /** 根据当前过滤条件过滤任务列表 */
  const filteredTodos = todos.filter(todo => {
    if (filter === 'active') return !todo.completed
    if (filter === 'completed') return todo.completed
    return true
  })

  /** 计算当前未完成的任务数量 */
  const activeCount = todos.filter(todo => !todo.completed).length

  /**
   * 处理输入框中的按键事件
   * 按下 Enter 键时触发添加任务
   */
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      addTodo()
    }
  }

  // ==================== 组件渲染 ====================
  
  return (
    // 主容器：渐变背景
    <div className="min-h-screen bg-gradient-to-br from-purple-400 via-pink-500 to-red-500 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* 页面标题 */}
        <h1 className="text-5xl font-bold text-white text-center mb-8 drop-shadow-lg">
          ✨ 我的待办事项
        </h1>

        {/* 错误提示面板 */}
        {error && (
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6 rounded-lg">
            <p className="font-semibold">⚠️ 错误</p>
            <p className="text-sm">{error}</p>
          </div>
        )}

        {/* 数据加载状态：显示加载动画 */}
        {loading ? (
          <div className="bg-white rounded-2xl shadow-2xl p-12 text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500"></div>
            <p className="text-gray-600 mt-4">正在加载任务...</p>
          </div>
        ) : (
          <>
            {/* 任务输入区域：支持输入新任务 */}
            <div className="bg-white rounded-2xl shadow-2xl p-6 mb-6">
              <div className="flex gap-3">
                {/* 输入框：输入新任务，支持 Enter 快捷键 */}
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="输入新任务..."
                  className="flex-1 px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-purple-500 transition-colors text-gray-700 placeholder-gray-400"
                />
                {/* 添加按钮 */}
                <button
                  onClick={addTodo}
                  className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-semibold rounded-lg hover:from-purple-600 hover:to-pink-600 transition-all transform hover:scale-105 active:scale-95 shadow-lg"
                >
                  添加
                </button>
              </div>
            </div>

            {/* 任务过滤按钮：按状态筛选任务 */}
            {/* 仅当有任务时显示过滤按钮 */}
            {todos.length > 0 && (
              <div className="flex gap-3 justify-center mb-6">
                {/* 全部任务过滤按钮 */}
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
                {/* 进行中的任务过滤按钮 */}
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
                {/* 已完成的任务过滤按钮 */}
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

            {/* 任务列表容器：展示过滤后的任务 */}
            <div className="bg-white rounded-2xl shadow-2xl p-6">
              {/* 空列表提示 */}
              {filteredTodos.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-gray-400 text-lg">
                    {todos.length === 0 ? '暂无任务，开始添加吧！ 🎯' : '没有符合条件的任务 📭'}
                  </p>
                </div>
              ) : (
                <ul className="space-y-3">
                  {/* 任务项循环渲染 */}
                  {filteredTodos.map((todo) => (
                    <li
                      key={todo.id}
                      className="flex items-center gap-3 bg-gradient-to-r from-gray-50 to-gray-100 p-4 rounded-lg hover:from-purple-50 hover:to-pink-50 transition-all group"
                    >
                      {/* 任务完成状态复选框 */}
                      <input
                        type="checkbox"
                        checked={todo.completed}
                        onChange={() => toggleComplete(todo.id)}
                        className="w-5 h-5 rounded border-2 border-gray-300 text-purple-600 focus:ring-2 focus:ring-purple-500 cursor-pointer"
                      />

                      {/* 任务内容：显示模式或编辑模式 */}
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
                        // 显示模式：显示任务文本和删除按钮
                        <>
                          {/* 任务文本：点击编辑，完成时显示删除线 */}
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
                          {/* 删除按钮 */}
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

            {/* 任务统计信息：显示未完成和总计数量 */}
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
