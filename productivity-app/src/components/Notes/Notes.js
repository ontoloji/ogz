import React, { useState } from 'react';
import './Notes.css';
import { v4 as uuidv4 } from 'uuid';
import { formatDateTime } from '../../utils/dateUtils';

const Notes = ({ notes, setNotes }) => {
  const [newNoteTitle, setNewNoteTitle] = useState('');
  const [newNoteContent, setNewNoteContent] = useState('');
  const [editingId, setEditingId] = useState(null);
  const [editTitle, setEditTitle] = useState('');
  const [editContent, setEditContent] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const addNote = () => {
    if (newNoteTitle.trim() && newNoteContent.trim()) {
      const note = {
        id: uuidv4(),
        title: newNoteTitle,
        content: newNoteContent,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString()
      };
      setNotes([note, ...notes]);
      setNewNoteTitle('');
      setNewNoteContent('');
    }
  };

  const startEdit = (note) => {
    setEditingId(note.id);
    setEditTitle(note.title);
    setEditContent(note.content);
  };

  const saveEdit = () => {
    if (editTitle.trim() && editContent.trim()) {
      setNotes(
        notes.map((note) =>
          note.id === editingId
            ? { ...note, title: editTitle, content: editContent, updatedAt: new Date().toISOString() }
            : note
        )
      );
      cancelEdit();
    }
  };

  const cancelEdit = () => {
    setEditingId(null);
    setEditTitle('');
    setEditContent('');
  };

  const deleteNote = (id) => {
    if (window.confirm('Bu notu silmek istediğinizden emin misiniz?')) {
      setNotes(notes.filter((n) => n.id !== id));
    }
  };

  const getFilteredNotes = () => {
    if (!searchQuery.trim()) return notes;
    const query = searchQuery.toLowerCase();
    return notes.filter(
      (note) =>
        note.title.toLowerCase().includes(query) ||
        note.content.toLowerCase().includes(query)
    );
  };

  const filteredNotes = getFilteredNotes();

  return (
    <div className="notes-container">
      <div className="notes-header">
        <h2>📝 Notlar</h2>
        <span className="notes-count">{notes.length} Not</span>
      </div>

      <div className="notes-search">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Notlarda ara..."
          className="search-input"
        />
      </div>

      <div className="note-input-section">
        <input
          type="text"
          value={newNoteTitle}
          onChange={(e) => setNewNoteTitle(e.target.value)}
          placeholder="Not başlığı..."
          className="note-title-input"
        />
        <textarea
          value={newNoteContent}
          onChange={(e) => setNewNoteContent(e.target.value)}
          placeholder="Not içeriği..."
          className="note-content-input"
          rows="4"
        />
        <button onClick={addNote} className="btn btn-primary">
          + Not Ekle
        </button>
      </div>

      <div className="notes-grid">
        {filteredNotes.length === 0 ? (
          <div className="empty-state">
            <p>📝 {searchQuery ? 'Not bulunamadı' : 'Henüz not yok'}</p>
            <p className="empty-subtitle">
              {searchQuery ? 'Farklı bir arama terimi deneyin' : 'Fikirlerinizi ve düşüncelerinizi not alın'}
            </p>
          </div>
        ) : (
          filteredNotes.map((note) => (
            <div key={note.id} className="note-card">
              {editingId === note.id ? (
                <div className="note-edit">
                  <input
                    type="text"
                    value={editTitle}
                    onChange={(e) => setEditTitle(e.target.value)}
                    className="edit-title-input"
                  />
                  <textarea
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    className="edit-content-input"
                    rows="6"
                  />
                  <div className="edit-buttons">
                    <button onClick={saveEdit} className="btn btn-success">
                      ✓ Kaydet
                    </button>
                    <button onClick={cancelEdit} className="btn btn-secondary">
                      ✕ İptal
                    </button>
                  </div>
                </div>
              ) : (
                <>
                  <div className="note-card-header">
                    <h3 className="note-title">{note.title}</h3>
                    <div className="note-actions">
                      <button
                        onClick={() => startEdit(note)}
                        className="btn-icon"
                        title="Düzenle"
                      >
                        ✏️
                      </button>
                      <button
                        onClick={() => deleteNote(note.id)}
                        className="btn-icon"
                        title="Sil"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                  <p className="note-content">{note.content}</p>
                  <div className="note-footer">
                    <span className="note-date">{formatDateTime(note.updatedAt)}</span>
                  </div>
                </>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Notes;
