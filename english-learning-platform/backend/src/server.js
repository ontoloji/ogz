const express = require('express');
const cors = require('cors');
const database = require('./database/db');

const wordsRouter = require('./routes/words');
const exercisesRouter = require('./routes/exercises');
const userRouter = require('./routes/user');
const categoriesRouter = require('./routes/categories');

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Request logging
app.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.path}`);
    next();
});

// Routes
app.use('/api/words', wordsRouter);
app.use('/api/exercises', exercisesRouter);
app.use('/api/user', userRouter);
app.use('/api/categories', categoriesRouter);

// Health check
app.get('/api/health', (req, res) => {
    res.json({
        status: 'OK',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Error:', err);
    res.status(err.status || 500).json({
        error: {
            message: err.message || 'Internal server error',
            status: err.status || 500
        }
    });
});

// 404 handler
app.use((req, res) => {
    res.status(404).json({
        error: {
            message: 'Route not found',
            status: 404
        }
    });
});

// Start server
async function startServer() {
    try {
        await database.connect();
        await database.initialize();

        app.listen(PORT, () => {
            console.log(`\n🚀 English Learning Platform API`);
            console.log(`📡 Server running on http://localhost:${PORT}`);
            console.log(`🏥 Health check: http://localhost:${PORT}/api/health\n`);
        });
    } catch (error) {
        console.error('Failed to start server:', error);
        process.exit(1);
    }
}

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('\nShutting down gracefully...');
    await database.close();
    process.exit(0);
});

startServer();

module.exports = app;
