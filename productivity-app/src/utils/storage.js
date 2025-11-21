import localforage from 'localforage';

// LocalForage configuration
localforage.config({
  name: 'ProductivityApp',
  storeName: 'app_data'
});

export const storage = {
  // Todos
  async getTodos() {
    return (await localforage.getItem('todos')) || [];
  },

  async saveTodos(todos) {
    await localforage.setItem('todos', todos);
  },

  // Projects
  async getProjects() {
    return (await localforage.getItem('projects')) || [];
  },

  async saveProjects(projects) {
    await localforage.setItem('projects', projects);
  },

  // Time entries
  async getTimeEntries() {
    return (await localforage.getItem('timeEntries')) || [];
  },

  async saveTimeEntries(entries) {
    await localforage.setItem('timeEntries', entries);
  },

  // Goals
  async getGoals() {
    return (await localforage.getItem('goals')) || [];
  },

  async saveGoals(goals) {
    await localforage.setItem('goals', goals);
  },

  // Notes
  async getNotes() {
    return (await localforage.getItem('notes')) || [];
  },

  async saveNotes(notes) {
    await localforage.setItem('notes', notes);
  },

  // Calendar events
  async getCalendarEvents() {
    return (await localforage.getItem('calendarEvents')) || [];
  },

  async saveCalendarEvents(events) {
    await localforage.setItem('calendarEvents', events);
  },

  // Blocked websites
  async getBlockedWebsites() {
    return (await localforage.getItem('blockedWebsites')) || [];
  },

  async saveBlockedWebsites(sites) {
    await localforage.setItem('blockedWebsites', sites);
  },

  // Settings
  async getSettings() {
    return (await localforage.getItem('settings')) || {
      pomodoroWork: 25,
      pomodoroShortBreak: 5,
      pomodoroLongBreak: 15,
      pomodoroSessions: 4
    };
  },

  async saveSettings(settings) {
    await localforage.setItem('settings', settings);
  },

  // Backup
  async exportData() {
    const data = {
      todos: await this.getTodos(),
      projects: await this.getProjects(),
      timeEntries: await this.getTimeEntries(),
      goals: await this.getGoals(),
      notes: await this.getNotes(),
      calendarEvents: await this.getCalendarEvents(),
      blockedWebsites: await this.getBlockedWebsites(),
      settings: await this.getSettings(),
      exportDate: new Date().toISOString()
    };
    return data;
  },

  async importData(data) {
    if (data.todos) await this.saveTodos(data.todos);
    if (data.projects) await this.saveProjects(data.projects);
    if (data.timeEntries) await this.saveTimeEntries(data.timeEntries);
    if (data.goals) await this.saveGoals(data.goals);
    if (data.notes) await this.saveNotes(data.notes);
    if (data.calendarEvents) await this.saveCalendarEvents(data.calendarEvents);
    if (data.blockedWebsites) await this.saveBlockedWebsites(data.blockedWebsites);
    if (data.settings) await this.saveSettings(data.settings);
  },

  async clearAll() {
    await localforage.clear();
  }
};

export default storage;
