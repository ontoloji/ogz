const database = require('./db');

async function seedDatabase() {
    try {
        await database.connect();

        console.log('🌱 Seeding database with sample data...');

        // Kelimeler ekle - Beginner seviyesi
        const beginnerWords = [
            { word: 'hello', meaning_tr: 'merhaba', meaning_en: 'a greeting', example: 'Hello! How are you?', level: 1, category: 1 },
            { word: 'goodbye', meaning_tr: 'hoşça kal', meaning_en: 'farewell', example: 'Goodbye, see you tomorrow!', level: 1, category: 1 },
            { word: 'please', meaning_tr: 'lütfen', meaning_en: 'polite request', example: 'Please help me.', level: 1, category: 1 },
            { word: 'thank you', meaning_tr: 'teşekkür ederim', meaning_en: 'expression of gratitude', example: 'Thank you for your help.', level: 1, category: 1 },
            { word: 'water', meaning_tr: 'su', meaning_en: 'liquid for drinking', example: 'I need a glass of water.', level: 1, category: 1 },
            { word: 'food', meaning_tr: 'yemek', meaning_en: 'something to eat', example: 'The food is delicious.', level: 1, category: 1 },
            { word: 'house', meaning_tr: 'ev', meaning_en: 'a building for living', example: 'I live in a big house.', level: 1, category: 1 },
            { word: 'family', meaning_tr: 'aile', meaning_en: 'parents and children', example: 'My family is very important to me.', level: 1, category: 1 },
            { word: 'friend', meaning_tr: 'arkadaş', meaning_en: 'a person you like', example: 'She is my best friend.', level: 1, category: 1 },
            { word: 'happy', meaning_tr: 'mutlu', meaning_en: 'feeling joy', example: 'I am very happy today.', level: 1, category: 1 }
        ];

        // Intermediate kelimeler
        const intermediateWords = [
            { word: 'schedule', meaning_tr: 'program, takvim', meaning_en: 'a plan of activities', example: 'Let me check my schedule.', level: 2, category: 2 },
            { word: 'deadline', meaning_tr: 'son tarih', meaning_en: 'final date for completion', example: 'The deadline is next Friday.', level: 2, category: 2 },
            { word: 'meeting', meaning_tr: 'toplantı', meaning_en: 'gathering of people', example: 'We have a meeting at 3 PM.', level: 2, category: 2 },
            { word: 'colleague', meaning_tr: 'meslektaş', meaning_en: 'coworker', example: 'My colleague helped me with the project.', level: 2, category: 2 },
            { word: 'presentation', meaning_tr: 'sunum', meaning_en: 'formal talk', example: 'I need to prepare a presentation.', level: 2, category: 2 },
            { word: 'achieve', meaning_tr: 'başarmak', meaning_en: 'to succeed in doing', example: 'We can achieve our goals.', level: 2, category: 3 },
            { word: 'develop', meaning_tr: 'geliştirmek', meaning_en: 'to grow or improve', example: 'We need to develop new skills.', level: 2, category: 5 },
            { word: 'implement', meaning_tr: 'uygulamak', meaning_en: 'to put into action', example: 'Let\'s implement this solution.', level: 2, category: 5 },
            { word: 'analyze', meaning_tr: 'analiz etmek', meaning_en: 'to examine in detail', example: 'We need to analyze the data.', level: 2, category: 3 },
            { word: 'strategy', meaning_tr: 'strateji', meaning_en: 'a plan of action', example: 'Our strategy is working well.', level: 2, category: 2 }
        ];

        // Advanced kelimeler
        const advancedWords = [
            { word: 'fundamental', meaning_tr: 'temel, esaslı', meaning_en: 'basic and important', example: 'This is a fundamental principle.', level: 3, category: 3 },
            { word: 'comprehensive', meaning_tr: 'kapsamlı', meaning_en: 'complete and thorough', example: 'We need a comprehensive solution.', level: 3, category: 3 },
            { word: 'subsequent', meaning_tr: 'sonraki, müteakip', meaning_en: 'coming after', example: 'Subsequent events proved him right.', level: 3, category: 3 },
            { word: 'ambiguous', meaning_tr: 'belirsiz, muğlak', meaning_en: 'unclear or uncertain', example: 'The instructions were ambiguous.', level: 3, category: 3 },
            { word: 'facilitate', meaning_tr: 'kolaylaştırmak', meaning_en: 'to make easier', example: 'This tool will facilitate the process.', level: 3, category: 2 }
        ];

        const allWords = [...beginnerWords, ...intermediateWords, ...advancedWords];

        for (const w of allWords) {
            await database.run(`
                INSERT INTO words (word, meaning_tr, meaning_en, example_sentence, level_id, category_id)
                VALUES (?, ?, ?, ?, ?, ?)
            `, [w.word, w.meaning_tr, w.meaning_en, w.example, w.level, w.category]);
        }

        console.log(`✅ Added ${allWords.length} words`);

        // Boşluk doldurma alıştırmaları ekle
        const fillBlankExercises = [
            {
                sentence: 'I need to ____ my schedule before making plans.',
                answer: 'check',
                options: ['check', 'make', 'see', 'look'],
                level: 1,
                category: 1
            },
            {
                sentence: 'The ____ for the project is next week.',
                answer: 'deadline',
                options: ['deadline', 'schedule', 'meeting', 'time'],
                level: 2,
                category: 2
            },
            {
                sentence: 'Can you ____ me with this problem?',
                answer: 'help',
                options: ['help', 'give', 'make', 'do'],
                level: 1,
                category: 1
            },
            {
                sentence: 'We need to ____ a comprehensive solution.',
                answer: 'develop',
                options: ['develop', 'make', 'create', 'build'],
                level: 2,
                category: 5
            },
            {
                sentence: 'This is a ____ principle of the theory.',
                answer: 'fundamental',
                options: ['fundamental', 'basic', 'simple', 'easy'],
                level: 3,
                category: 3
            },
            {
                sentence: 'I am very ____ to see you.',
                answer: 'happy',
                options: ['happy', 'sad', 'angry', 'tired'],
                level: 1,
                category: 1
            },
            {
                sentence: 'The instructions were very ____.',
                answer: 'clear',
                options: ['clear', 'ambiguous', 'simple', 'difficult'],
                level: 2,
                category: 3
            }
        ];

        for (const ex of fillBlankExercises) {
            const result = await database.run(`
                INSERT INTO fill_blank_exercises (sentence, correct_answer, blank_position, level_id, category_id)
                VALUES (?, ?, ?, ?, ?)
            `, [ex.sentence, ex.answer, ex.sentence.indexOf('____'), ex.level, ex.category]);

            for (const option of ex.options) {
                await database.run(`
                    INSERT INTO fill_blank_options (exercise_id, option_text, is_correct)
                    VALUES (?, ?, ?)
                `, [result.id, option, option === ex.answer ? 1 : 0]);
            }
        }

        console.log(`✅ Added ${fillBlankExercises.length} fill-in-the-blank exercises`);

        console.log('✨ Database seeding completed successfully!');

    } catch (error) {
        console.error('❌ Error seeding database:', error);
    } finally {
        await database.close();
    }
}

// Eğer direkt çalıştırılıyorsa seed'i çalıştır
if (require.main === module) {
    seedDatabase();
}

module.exports = seedDatabase;
