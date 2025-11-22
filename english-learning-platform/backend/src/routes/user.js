const express = require('express');
const router = express.Router();
const database = require('../database/db');

// Kullanıcı profilini getir
router.get('/:id', async (req, res, next) => {
    try {
        const { id } = req.params;

        const user = await database.get(`
            SELECT u.id, u.username, u.email, u.daily_goal, u.created_at, u.last_login,
                   l.name as current_level
            FROM users u
            LEFT JOIN levels l ON u.current_level_id = l.id
            WHERE u.id = ?
        `, [id]);

        if (!user) {
            return res.status(404).json({
                success: false,
                error: 'User not found'
            });
        }

        res.json({
            success: true,
            data: user
        });
    } catch (error) {
        next(error);
    }
});

// Kullanıcı istatistiklerini getir
router.get('/:id/stats', async (req, res, next) => {
    try {
        const { id } = req.params;

        const stats = await database.get(`
            SELECT * FROM user_statistics WHERE user_id = ?
        `, [id]);

        res.json({
            success: true,
            data: stats || {
                user_id: id,
                total_words_learned: 0,
                total_exercises: 0,
                correct_answers: 0,
                total_attempts: 0,
                accuracy_percentage: 0
            }
        });
    } catch (error) {
        next(error);
    }
});

// Günlük ilerlemeyi getir
router.get('/:id/progress', async (req, res, next) => {
    try {
        const { id } = req.params;
        const { days = 7 } = req.query;

        const progress = await database.all(`
            SELECT date, words_learned, exercises_completed, correct_answers, total_answers, goal_achieved
            FROM daily_progress
            WHERE user_id = ?
            ORDER BY date DESC
            LIMIT ?
        `, [id, parseInt(days)]);

        // Bugünün ilerlemesi
        const today = new Date().toISOString().split('T')[0];
        const todayProgress = await database.get(`
            SELECT * FROM daily_progress WHERE user_id = ? AND date = ?
        `, [id, today]);

        const user = await database.get('SELECT daily_goal FROM users WHERE id = ?', [id]);

        res.json({
            success: true,
            data: {
                today: todayProgress || {
                    date: today,
                    words_learned: 0,
                    exercises_completed: 0,
                    correct_answers: 0,
                    total_answers: 0,
                    goal_achieved: false
                },
                daily_goal: user?.daily_goal || 10,
                history: progress
            }
        });
    } catch (error) {
        next(error);
    }
});

// Günlük hedef güncelle
router.put('/:id/goal', async (req, res, next) => {
    try {
        const { id } = req.params;
        const { daily_goal } = req.body;

        if (!daily_goal || daily_goal < 1) {
            return res.status(400).json({
                success: false,
                error: 'Invalid daily goal'
            });
        }

        await database.run(`
            UPDATE users SET daily_goal = ? WHERE id = ?
        `, [daily_goal, id]);

        res.json({
            success: true,
            data: {
                message: 'Daily goal updated',
                daily_goal
            }
        });
    } catch (error) {
        next(error);
    }
});

// Öğrenilen kelimeleri getir
router.get('/:id/learned-words', async (req, res, next) => {
    try {
        const { id } = req.params;
        const { limit = 50, offset = 0 } = req.query;

        const words = await database.all(`
            SELECT w.*, uw.learned_at, uw.mastery_level, uw.review_count
            FROM user_words uw
            JOIN words w ON uw.word_id = w.id
            WHERE uw.user_id = ?
            ORDER BY uw.learned_at DESC
            LIMIT ? OFFSET ?
        `, [id, parseInt(limit), parseInt(offset)]);

        res.json({
            success: true,
            data: words,
            count: words.length
        });
    } catch (error) {
        next(error);
    }
});

// Kelime öğrenildi olarak işaretle
router.post('/:id/learn-word', async (req, res, next) => {
    try {
        const { id } = req.params;
        const { word_id } = req.body;

        if (!word_id) {
            return res.status(400).json({
                success: false,
                error: 'Word ID is required'
            });
        }

        // Daha önce öğrenilmiş mi kontrol et
        const existing = await database.get(`
            SELECT * FROM user_words WHERE user_id = ? AND word_id = ?
        `, [id, word_id]);

        if (existing) {
            // Mastery level'i artır
            await database.run(`
                UPDATE user_words
                SET mastery_level = mastery_level + 1,
                    review_count = review_count + 1,
                    last_reviewed = CURRENT_TIMESTAMP
                WHERE user_id = ? AND word_id = ?
            `, [id, word_id]);
        } else {
            // Yeni kelime olarak ekle
            await database.run(`
                INSERT INTO user_words (user_id, word_id)
                VALUES (?, ?)
            `, [id, word_id]);

            // Günlük ilerlemeyi güncelle
            const today = new Date().toISOString().split('T')[0];
            const dailyProgress = await database.get(`
                SELECT * FROM daily_progress WHERE user_id = ? AND date = ?
            `, [id, today]);

            if (dailyProgress) {
                await database.run(`
                    UPDATE daily_progress
                    SET words_learned = words_learned + 1
                    WHERE user_id = ? AND date = ?
                `, [id, today]);
            } else {
                await database.run(`
                    INSERT INTO daily_progress (user_id, date, words_learned)
                    VALUES (?, ?, 1)
                `, [id, today]);
            }
        }

        res.json({
            success: true,
            data: {
                message: 'Word marked as learned'
            }
        });
    } catch (error) {
        next(error);
    }
});

module.exports = router;
