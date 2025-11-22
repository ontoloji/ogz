const express = require('express');
const router = express.Router();
const database = require('../database/db');

// Boşluk doldurma alıştırması getir
router.get('/fill-blank', async (req, res, next) => {
    try {
        const { level, category, count = 5 } = req.query;

        let query = `
            SELECT fbe.*, l.name as level_name, c.name as category_name
            FROM fill_blank_exercises fbe
            LEFT JOIN levels l ON fbe.level_id = l.id
            LEFT JOIN categories c ON fbe.category_id = c.id
            WHERE 1=1
        `;
        const params = [];

        if (level) {
            query += ' AND l.name = ?';
            params.push(level);
        }

        if (category) {
            query += ' AND c.name = ?';
            params.push(category);
        }

        query += ' ORDER BY RANDOM() LIMIT ?';
        params.push(parseInt(count));

        const exercises = await database.all(query, params);

        // Her alıştırma için seçenekleri getir
        const exercisesWithOptions = await Promise.all(
            exercises.map(async (exercise) => {
                const options = await database.all(`
                    SELECT option_text, is_correct
                    FROM fill_blank_options
                    WHERE exercise_id = ?
                    ORDER BY RANDOM()
                `, [exercise.id]);

                return {
                    id: exercise.id,
                    sentence: exercise.sentence,
                    blank_position: exercise.blank_position,
                    level: exercise.level_name,
                    category: exercise.category_name,
                    options: options.map(opt => opt.option_text),
                    correct_answer: options.find(opt => opt.is_correct === 1)?.option_text
                };
            })
        );

        res.json({
            success: true,
            data: exercisesWithOptions,
            count: exercisesWithOptions.length
        });
    } catch (error) {
        next(error);
    }
});

// Kelime eşleştirme alıştırması getir
router.get('/match-meaning', async (req, res, next) => {
    try {
        const { level, count = 5 } = req.query;

        let query = `
            SELECT w.id, w.word, w.meaning_tr, l.name as level_name
            FROM words w
            LEFT JOIN levels l ON w.level_id = l.id
            WHERE 1=1
        `;
        const params = [];

        if (level) {
            query += ' AND l.name = ?';
            params.push(level);
        }

        query += ' ORDER BY RANDOM() LIMIT ?';
        params.push(parseInt(count));

        const words = await database.all(query, params);

        // Anlamları karıştır
        const meanings = words.map(w => ({
            id: w.id,
            meaning: w.meaning_tr
        })).sort(() => Math.random() - 0.5);

        const exercise = {
            words: words.map(w => ({
                id: w.id,
                word: w.word,
                level: w.level_name
            })),
            meanings: meanings,
            type: 'match-meaning'
        };

        res.json({
            success: true,
            data: exercise
        });
    } catch (error) {
        next(error);
    }
});

// Alıştırma cevabını kontrol et ve kaydet
router.post('/submit', async (req, res, next) => {
    try {
        const { user_id, exercise_type, exercise_id, user_answer, correct_answer, time_spent } = req.body;

        if (!user_id || !exercise_type || !user_answer) {
            return res.status(400).json({
                success: false,
                error: 'Missing required fields'
            });
        }

        const is_correct = user_answer.toLowerCase().trim() === correct_answer.toLowerCase().trim();

        // Cevabı kaydet
        const result = await database.run(`
            INSERT INTO exercise_attempts (user_id, exercise_type, exercise_id, user_answer, is_correct, time_spent)
            VALUES (?, ?, ?, ?, ?, ?)
        `, [user_id, exercise_type, exercise_id || 0, user_answer, is_correct ? 1 : 0, time_spent || 0]);

        // Günlük ilerlemeyi güncelle
        const today = new Date().toISOString().split('T')[0];

        const dailyProgress = await database.get(`
            SELECT * FROM daily_progress
            WHERE user_id = ? AND date = ?
        `, [user_id, today]);

        if (dailyProgress) {
            await database.run(`
                UPDATE daily_progress
                SET exercises_completed = exercises_completed + 1,
                    correct_answers = correct_answers + ?,
                    total_answers = total_answers + 1
                WHERE user_id = ? AND date = ?
            `, [is_correct ? 1 : 0, user_id, today]);
        } else {
            await database.run(`
                INSERT INTO daily_progress (user_id, date, exercises_completed, correct_answers, total_answers)
                VALUES (?, ?, 1, ?, 1)
            `, [user_id, today, is_correct ? 1 : 0]);
        }

        res.json({
            success: true,
            data: {
                is_correct,
                message: is_correct ? 'Doğru cevap!' : 'Yanlış cevap',
                correct_answer: correct_answer
            }
        });
    } catch (error) {
        next(error);
    }
});

// Yeni boşluk doldurma alıştırması ekle
router.post('/fill-blank', async (req, res, next) => {
    try {
        const { sentence, correct_answer, blank_position, options, level_id, category_id, word_id } = req.body;

        if (!sentence || !correct_answer || !options || options.length < 2) {
            return res.status(400).json({
                success: false,
                error: 'Missing required fields or insufficient options'
            });
        }

        const result = await database.run(`
            INSERT INTO fill_blank_exercises (sentence, correct_answer, blank_position, level_id, category_id, word_id)
            VALUES (?, ?, ?, ?, ?, ?)
        `, [sentence, correct_answer, blank_position, level_id, category_id, word_id]);

        // Seçenekleri ekle
        for (const option of options) {
            await database.run(`
                INSERT INTO fill_blank_options (exercise_id, option_text, is_correct)
                VALUES (?, ?, ?)
            `, [result.id, option, option === correct_answer ? 1 : 0]);
        }

        res.status(201).json({
            success: true,
            data: {
                id: result.id,
                message: 'Exercise created successfully'
            }
        });
    } catch (error) {
        next(error);
    }
});

module.exports = router;
