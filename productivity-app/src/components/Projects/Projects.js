import React, { useState } from 'react';
import './Projects.css';
import { v4 as uuidv4 } from 'uuid';

const Projects = ({ projects, setProjects, todos }) => {
  const [newProject, setNewProject] = useState('');
  const [newProjectColor, setNewProjectColor] = useState('#667eea');
  const [editingId, setEditingId] = useState(null);
  const [editName, setEditName] = useState('');

  const colors = [
    '#667eea', '#764ba2', '#48bb78', '#f56565',
    '#ed8936', '#4299e1', '#9f7aea', '#38b2ac',
    '#ed64a6', '#ecc94b'
  ];

  const addProject = () => {
    if (newProject.trim()) {
      const project = {
        id: uuidv4(),
        name: newProject,
        color: newProjectColor,
        createdAt: new Date().toISOString()
      };
      setProjects([...projects, project]);
      setNewProject('');
      setNewProjectColor('#667eea');
    }
  };

  const deleteProject = (id) => {
    if (window.confirm('Bu projeyi silmek istediğinizden emin misiniz?')) {
      setProjects(projects.filter((p) => p.id !== id));
    }
  };

  const startEdit = (project) => {
    setEditingId(project.id);
    setEditName(project.name);
  };

  const saveEdit = () => {
    if (editName.trim()) {
      setProjects(
        projects.map((p) =>
          p.id === editingId ? { ...p, name: editName } : p
        )
      );
      setEditingId(null);
      setEditName('');
    }
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditName('');
  };

  const getProjectStats = (projectId) => {
    const projectTodos = todos.filter((t) => t.projectId === projectId);
    return {
      total: projectTodos.length,
      completed: projectTodos.filter((t) => t.completed).length,
      active: projectTodos.filter((t) => !t.completed).length
    };
  };

  return (
    <div className="projects-container">
      <div className="projects-header">
        <h2>📁 Projeler</h2>
        <span className="project-count">{projects.length} Proje</span>
      </div>

      <div className="project-input-section">
        <input
          type="text"
          value={newProject}
          onChange={(e) => setNewProject(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && addProject()}
          placeholder="Yeni proje adı..."
          className="project-input"
        />
        <div className="color-picker">
          {colors.map((color) => (
            <button
              key={color}
              className={`color-option ${newProjectColor === color ? 'active' : ''}`}
              style={{ backgroundColor: color }}
              onClick={() => setNewProjectColor(color)}
              title="Renk seç"
            />
          ))}
        </div>
        <button onClick={addProject} className="btn btn-primary">
          + Proje Ekle
        </button>
      </div>

      <div className="projects-grid">
        {projects.length === 0 ? (
          <div className="empty-state">
            <p>📋 Henüz proje yok</p>
            <p className="empty-subtitle">Görevlerinizi organize etmek için proje oluşturun</p>
          </div>
        ) : (
          projects.map((project) => {
            const stats = getProjectStats(project.id);
            const completionRate = stats.total > 0
              ? Math.round((stats.completed / stats.total) * 100)
              : 0;

            return (
              <div
                key={project.id}
                className="project-card"
                style={{ borderLeft: `4px solid ${project.color}` }}
              >
                {editingId === project.id ? (
                  <div className="project-edit">
                    <input
                      type="text"
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && saveEdit()}
                      className="edit-input"
                      autoFocus
                    />
                    <div className="edit-buttons">
                      <button onClick={saveEdit} className="btn-save">✓</button>
                      <button onClick={cancelEdit} className="btn-cancel">✕</button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className="project-header">
                      <h3 className="project-name">{project.name}</h3>
                      <div className="project-actions">
                        <button
                          onClick={() => startEdit(project)}
                          className="btn-icon"
                          title="Düzenle"
                        >
                          ✏️
                        </button>
                        <button
                          onClick={() => deleteProject(project.id)}
                          className="btn-icon"
                          title="Sil"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>

                    <div className="project-stats">
                      <div className="stat-item">
                        <span className="stat-label">Toplam</span>
                        <span className="stat-value">{stats.total}</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Aktif</span>
                        <span className="stat-value">{stats.active}</span>
                      </div>
                      <div className="stat-item">
                        <span className="stat-label">Tamamlanan</span>
                        <span className="stat-value">{stats.completed}</span>
                      </div>
                    </div>

                    <div className="progress-bar-container">
                      <div className="progress-bar-bg">
                        <div
                          className="progress-bar-fill"
                          style={{
                            width: `${completionRate}%`,
                            backgroundColor: project.color
                          }}
                        />
                      </div>
                      <span className="progress-text">{completionRate}% Tamamlandı</span>
                    </div>
                  </>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default Projects;
