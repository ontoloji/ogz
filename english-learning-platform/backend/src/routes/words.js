const express = require('express');
const router = express.Router();
const database = require('../database/db');

// Tüm kelimeleri getir (filtreleme ile)
router.get('/', async (req, res, next) => {
    try {
        const { level, category, limit = 50, offset = 0 } = req.query;

        let query = `
            SELECT w.*, l.name as level_name, c.name as category_name
            FROM words w
            LEFT JOIN levels l ON w.level_id = l.id
            LEFT JOIN categories c ON w.category_id = c.id
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

        query += ' ORDER BY w.created_at DESC LIMIT ? OFFSET ?';
        params.push(parseInt(limit), parseInt(offset));

        const words = await database.all(query, params);
        res.json({
            success: true,
            data: words,
            count: words.length
        });
    } catch (error) {
        next(error);
    }
});

// Rastgele kelimeler getir (günlük öğrenme için)
router.get('/random', async (req, res, next) => {
    try {
        const { level, count = 10 } = req.query;

        let query = `
            SELECT w.*, l.name as level_name, c.name as category_name
            FROM words w
            LEFT JOIN levels l ON w.level_id = l.id
            LEFT JOIN categories c ON w.category_id = c.id
        `;
        const params = [];

        if (level) {
            query += ' WHERE l.name = ?';
            params.push(level);
        }

        query += ' ORDER BY RANDOM() LIMIT ?';
        params.push(parseInt(count));

        const words = await database.all(query, params);
        res.json({
            success: true,
            data: words,
            count: words.length
        });
    } catch (error) {
        next(error);
    }
});

// Belirli bir kelimeyi getir
router.get('/:id', async (req, res, next) => {
    try {
        const { id } = req.params;

        const word = await database.get(`
            SELECT w.*, l.name as level_name, c.name as category_name
            FROM words w
            LEFT JOIN levels l ON w.level_id = l.id
            LEFT JOIN categories c ON w.category_id = c.id
            WHERE w.id = ?
        `, [id]);

        if (!word) {
            return res.status(404).json({
                success: false,
                error: 'Word not found'
            });
        }

        res.json({
            success: true,
            data: word
        });
    } catch (error) {
        next(error);
    }
});

// Yeni kelime ekle
router.post('/', async (req, res, next) => {
    try {
        const { word, meaning_tr, meaning_en, example_sentence, pronunciation, level_id, category_id } = req.body;

        if (!word || !meaning_tr) {
            return res.status(400).json({
                success: false,
                error: 'Word and Turkish meaning are required'
            });
        }

        const result = await database.run(`
            INSERT INTO words (word, meaning_tr, meaning_en, example_sentence, pronunciation, level_id, category_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        `, [word, meaning_tr, meaning_en, example_sentence, pronunciation, level_id, category_id]);

        res.status(201).json({
            success: true,
            data: {
                id: result.id,
                message: 'Word added successfully'
            }
        });
    } catch (error) {
        next(error);
    }
});

module.exports = router;
