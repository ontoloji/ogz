import React, { useState } from 'react';
import './TodoList.css';
import { v4 as uuidv4 } from 'uuid';

const TodoList = ({ todos, setTodos, projects }) => {
  const [newTodo, setNewTodo] = useState('');
  const [filter, setFilter] = useState('all'); // all, active, completed
  const [selectedProject, setSelectedProject] = useState('');
  const [priority, setPriority] = useState('medium');

  const addTodo = () => {
    if (newTodo.trim()) {
      const todo = {
        id: uuidv4(),
        text: newTodo,
        completed: false,
        priority,
        projectId: selectedProject || null,
        createdAt: new Date().toISOString(),
        dueDate: null
      };
      setTodos([...todos, todo]);
      setNewTodo('');
      setPriority('medium');
    }
  };

  const toggleTodo = (id) => {
    setTodos(
      todos.map((todo) =>
        todo.id === id
          ? { ...todo, completed: !todo.completed, completedAt: !todo.completed ? new Date().toISOString() : null }
          : todo
      )
    );
  };

  const deleteTodo = (id) => {
    setTodos(todos.filter((todo) => todo.id !== id));
  };

  const updateTodo = (id, updates) => {
    setTodos(
      todos.map((todo) =>
        todo.id === id ? { ...todo, ...updates } : todo
      )
    );
  };

  const getFilteredTodos = () => {
    let filtered = todos;

    // Filter by completion status
    if (filter === 'active') {
      filtered = filtered.filter((todo) => !todo.completed);
    } else if (filter === 'completed') {
      filtered = filtered.filter((todo) => todo.completed);
    }

    // Filter by project
    if (selectedProject) {
      filtered = filtered.filter((todo) => todo.projectId === selectedProject);
    }

    return filtered;
  };

  const getPriorityBadge = (priority) => {
    const badges = {
      high: { class: 'badge-danger', text: 'Yüksek' },
      medium: { class: 'badge-warning', text: 'Orta' },
      low: { class: 'badge-success', text: 'Düşük' }
    };
    return badges[priority] || badges.medium;
  };

  const getProjectName = (projectId) => {
    const project = projects.find((p) => p.id === projectId);
    return project ? project.name : 'Genel';
  };

  const filteredTodos = getFilteredTodos();
  const stats = {
    total: todos.length,
    active: todos.filter((t) => !t.completed).length,
    completed: todos.filter((t) => t.completed).length
  };

  return (
    <div className="todo-list-container">
      <div className="todo-header">
        <h2>📝 Görev Listesi</h2>
        <div className="todo-stats">
          <span className="stat">
            <strong>{stats.active}</strong> Aktif
          </span>
          <span className="stat">
            <strong>{stats.completed}</strong> Tamamlandı
          </span>
          <span className="stat">
            <strong>{stats.total}</strong> Toplam
          </span>
        </div>
      </div>

      <div className="todo-input-section">
        <div className="todo-input-row">
          <input
            type="text"
            value={newTodo}
            onChange={(e) => setNewTodo(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && addTodo()}
            placeholder="Yeni görev ekle..."
            className="todo-input"
          />
          <button onClick={addTodo} className="btn btn-primary">
            + Ekle
          </button>
        </div>
        <div className="todo-options-row">
          <select
            value={priority}
            onChange={(e) => setPriority(e.target.value)}
            className="todo-select"
          >
            <option value="low">Düşük Öncelik</option>
            <option value="medium">Orta Öncelik</option>
            <option value="high">Yüksek Öncelik</option>
          </select>
          <select
            value={selectedProject}
            onChange={(e) => setSelectedProject(e.target.value)}
            className="todo-select"
          >
            <option value="">Proje Seç (Opsiyonel)</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="todo-filters">
        <button
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          Tümü ({stats.total})
        </button>
        <button
          className={`filter-btn ${filter === 'active' ? 'active' : ''}`}
          onClick={() => setFilter('active')}
        >
          Aktif ({stats.active})
        </button>
        <button
          className={`filter-btn ${filter === 'completed' ? 'active' : ''}`}
          onClick={() => setFilter('completed')}
        >
          Tamamlanan ({stats.completed})
        </button>
      </div>

      <div className="todos-list">
        {filteredTodos.length === 0 ? (
          <div className="empty-state">
            <p>📋 Henüz görev yok</p>
            <p className="empty-subtitle">Yukarıdan yeni bir görev ekleyin</p>
          </div>
        ) : (
          filteredTodos.map((todo) => {
            const priorityBadge = getPriorityBadge(todo.priority);
            return (
              <div
                key={todo.id}
                className={`todo-item ${todo.completed ? 'completed' : ''} priority-${todo.priority}`}
              >
                <div className="todo-checkbox">
                  <input
                    type="checkbox"
                    checked={todo.completed}
                    onChange={() => toggleTodo(todo.id)}
                    id={`todo-${todo.id}`}
                  />
                  <label htmlFor={`todo-${todo.id}`} className="checkbox-label"></label>
                </div>
                <div className="todo-content">
                  <div className="todo-text">{todo.text}</div>
                  <div className="todo-meta">
                    <span className={`badge ${priorityBadge.class}`}>
                      {priorityBadge.text}
                    </span>
                    {todo.projectId && (
                      <span className="badge badge-info">
                        📁 {getProjectName(todo.projectId)}
                      </span>
                    )}
                  </div>
                </div>
                <button
                  className="btn-delete"
                  onClick={() => deleteTodo(todo.id)}
                  title="Sil"
                >
                  🗑️
                </button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default TodoList;
