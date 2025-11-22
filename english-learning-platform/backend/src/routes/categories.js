const express = require('express');
const router = express.Router();
const database = require('../database/db');

// Tüm kategorileri getir
router.get('/', async (req, res, next) => {
    try {
        const categories = await database.all(`
            SELECT c.*, COUNT(w.id) as word_count
            FROM categories c
            LEFT JOIN words w ON c.id = w.category_id
            GROUP BY c.id
            ORDER BY c.name
        `);

        res.json({
            success: true,
            data: categories
        });
    } catch (error) {
        next(error);
    }
});

// Tüm seviyeleri getir
router.get('/levels', async (req, res, next) => {
    try {
        const levels = await database.all(`
            SELECT l.*, COUNT(w.id) as word_count
            FROM levels l
            LEFT JOIN words w ON l.id = w.level_id
            GROUP BY l.id
            ORDER BY l.order_num
        `);

        res.json({
            success: true,
            data: levels
        });
    } catch (error) {
        next(error);
    }
});

module.exports = router;
