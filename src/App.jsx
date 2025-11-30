import { useState, useEffect } from 'react'

const STORAGE_KEY = 'todoList'

function App() {
  // 从 localStorage 读取初始数据
  const [todos, setTodos] = useState(() => {
    const savedTodos = localStorage.getItem(STORAGE_KEY)
    return savedTodos ? JSON.parse(savedTodos) : []
  })
  const [inputValue, setInputValue] = useState('')

  // 每当 todos 变化时，自动保存到 localStorage
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(todos))
  }, [todos])

  // 添加任务
  const addTodo = () => {
    if (inputValue.trim() !== '') {
      setTodos([...todos, { id: Date.now(), text: inputValue }])
      setInputValue('')
    }
  }

  // 删除任务
  const deleteTodo = (id) => {
    setTodos(todos.filter(todo => todo.id !== id))
  }

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

        {/* 任务列表 */}
        <div className="bg-white rounded-2xl shadow-2xl p-6">
          {todos.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-400 text-lg">暂无任务，开始添加吧！ 🎯</p>
            </div>
          ) : (
            <ul className="space-y-3">
              {todos.map((todo) => (
                <li
                  key={todo.id}
                  className="flex items-center justify-between bg-gradient-to-r from-gray-50 to-gray-100 p-4 rounded-lg hover:from-purple-50 hover:to-pink-50 transition-all group"
                >
                  <span className="text-gray-700 text-lg flex-1">
                    {todo.text}
                  </span>
                  <button
                    onClick={() => deleteTodo(todo.id)}
                    className="ml-4 px-4 py-2 bg-red-500 text-white font-medium rounded-lg hover:bg-red-600 transition-all transform hover:scale-105 active:scale-95 shadow-md opacity-90 group-hover:opacity-100"
                  >
                    删除
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* 统计信息 */}
        {todos.length > 0 && (
          <div className="mt-6 text-center text-white text-lg font-semibold drop-shadow">
            共 {todos.length} 个任务
          </div>
        )}
      </div>
    </div>
  )
}

export default App
