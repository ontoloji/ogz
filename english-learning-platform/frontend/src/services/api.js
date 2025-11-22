import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

// Words API
export const getWords = (params = {}) => api.get('/words', { params });
export const getRandomWords = (params = {}) => api.get('/words/random', { params });
export const getWord = (id) => api.get(`/words/${id}`);
export const createWord = (data) => api.post('/words', data);

// Exercises API
export const getFillBlankExercises = (params = {}) => api.get('/exercises/fill-blank', { params });
export const getMatchMeaningExercise = (params = {}) => api.get('/exercises/match-meaning', { params });
export const submitExercise = (data) => api.post('/exercises/submit', data);
export const createFillBlankExercise = (data) => api.post('/exercises/fill-blank', data);

// User API
export const getUserProfile = (userId) => api.get(`/user/${userId}`);
export const getUserStats = (userId) => api.get(`/user/${userId}/stats`);
export const getUserProgress = (userId, params = {}) => api.get(`/user/${userId}/progress`, { params });
export const updateDailyGoal = (userId, dailyGoal) => api.put(`/user/${userId}/goal`, { daily_goal: dailyGoal });
export const getLearnedWords = (userId, params = {}) => api.get(`/user/${userId}/learned-words`, { params });
export const markWordAsLearned = (userId, wordId) => api.post(`/user/${userId}/learn-word`, { word_id: wordId });

// Categories API
export const getCategories = () => api.get('/categories');
export const getLevels = () => api.get('/categories/levels');

export default api;
