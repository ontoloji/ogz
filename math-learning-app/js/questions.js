/**
 * Soru Bankası ve Üretici Sistemi
 * Dinamik soru üretimi ve çözüm adımları
 */

const QuestionGenerator = {
    /**
     * Verilen konu için soru üret
     */
    generate(subjectId, topicId, difficulty) {
        const methodName = `generate_${topicId}`;

        if (typeof this[methodName] === 'function') {
            const question = this[methodName](difficulty);
            question.subjectId = subjectId;
            question.topicId = topicId;
            question.difficulty = difficulty;
            return question;
        }

        // Varsayılan soru (eğer üretici yoksa)
        return this.generateDefaultQuestion(subjectId, topicId, difficulty);
    },

    /**
     * Kesir toplama soruları
     */
    generate_fraction_addition(difficulty) {
        let num1, den1, num2, den2;

        if (difficulty === 'easy') {
            // Aynı paydalar
            den1 = den2 = Utils.randomInt(2, 10);
            num1 = Utils.randomInt(1, den1 - 1);
            num2 = Utils.randomInt(1, den1 - num1);
        } else if (difficulty === 'medium') {
            // Farklı paydalar (katları)
            den1 = Utils.randomInt(2, 6);
            den2 = den1 * Utils.randomInt(2, 4);
            num1 = Utils.randomInt(1, den1 - 1);
            num2 = Utils.randomInt(1, den2 - 1);
        } else {
            // Zor - tamamen farklı paydalar
            den1 = Utils.randomInt(3, 12);
            den2 = Utils.randomInt(3, 12);
            while (den2 === den1) den2 = Utils.randomInt(3, 12);
            num1 = Utils.randomInt(1, den1 - 1);
            num2 = Utils.randomInt(1, den2 - 1);
        }

        const lcm = Utils.lcm(den1, den2);
        const newNum1 = num1 * (lcm / den1);
        const newNum2 = num2 * (lcm / den2);
        const resultNum = newNum1 + newNum2;
        const simplified = Utils.simplifyFraction(resultNum, lcm);

        return {
            type: 'multiple-choice',
            question: `<div class="math-expression">${num1}/${den1} + ${num2}/${den2} = ?</div>`,
            correctAnswer: `${simplified.numerator}/${simplified.denominator}`,
            options: this.generateFractionOptions(simplified.numerator, simplified.denominator),
            hint: 'Paydaları eşitle, payları topla!',
            solution: [
                `Paydaları eşitlemeliyiz. EKOK(${den1}, ${den2}) = ${lcm}`,
                `${num1}/${den1} = ${newNum1}/${lcm}`,
                `${num2}/${den2} = ${newNum2}/${lcm}`,
                `${newNum1}/${lcm} + ${newNum2}/${lcm} = ${resultNum}/${lcm}`,
                simplified.numerator !== resultNum ?
                    `Sadeleştirme: ${resultNum}/${lcm} = ${simplified.numerator}/${simplified.denominator}` :
                    'Cevap zaten sadeleştirilmiş halde.'
            ],
            visualizationType: 'fractionCircles',
            visualizationData: { fraction1: {num: num1, den: den1}, fraction2: {num: num2, den: den2} }
        };
    },

    /**
     * Kesir çarpma soruları
     */
    generate_fraction_multiplication(difficulty) {
        let num1, den1, num2, den2;

        if (difficulty === 'easy') {
            num1 = Utils.randomInt(1, 5);
            den1 = Utils.randomInt(2, 8);
            num2 = Utils.randomInt(1, 5);
            den2 = Utils.randomInt(2, 8);
        } else {
            num1 = Utils.randomInt(1, 12);
            den1 = Utils.randomInt(2, 15);
            num2 = Utils.randomInt(1, 12);
            den2 = Utils.randomInt(2, 15);
        }

        const resultNum = num1 * num2;
        const resultDen = den1 * den2;
        const simplified = Utils.simplifyFraction(resultNum, resultDen);

        return {
            type: 'multiple-choice',
            question: `<div class="math-expression">${num1}/${den1} × ${num2}/${den2} = ?</div>`,
            correctAnswer: `${simplified.numerator}/${simplified.denominator}`,
            options: this.generateFractionOptions(simplified.numerator, simplified.denominator),
            hint: 'Pay ile payı, payda ile paydayı çarp!',
            solution: [
                `Paylar: ${num1} × ${num2} = ${resultNum}`,
                `Paydalar: ${den1} × ${den2} = ${resultDen}`,
                `Sonuç: ${resultNum}/${resultDen}`,
                simplified.numerator !== resultNum ?
                    `Sadeleştirme: ${resultNum}/${resultDen} = ${simplified.numerator}/${simplified.denominator}` :
                    'Cevap zaten sadeleştirilmiş halde.'
            ],
            visualizationType: 'fractionRectangles',
            visualizationData: { fraction1: {num: num1, den: den1}, fraction2: {num: num2, den: den2} }
        };
    },

    /**
     * Basit denklem soruları
     */
    generate_simple_equations(difficulty) {
        let a, b, x;

        if (difficulty === 'easy') {
            x = Utils.randomInt(1, 10);
            a = Utils.randomInt(2, 5);
            b = Utils.randomInt(1, 20);
        } else {
            x = Utils.randomInt(1, 20);
            a = Utils.randomInt(2, 10);
            b = Utils.randomInt(10, 50);
        }

        const result = a * x + b;
        const operation = Utils.randomChoice(['+', '-']);

        if (operation === '+') {
            return {
                type: 'input',
                question: `<div class="math-expression">x + ${b} = ${result}</div><div>x = ?</div>`,
                correctAnswer: x,
                hint: 'Her iki taraftan da aynı sayıyı çıkar!',
                solution: [
                    `x + ${b} = ${result}`,
                    `x = ${result} - ${b}`,
                    `x = ${x}`
                ],
                visualizationType: 'balance',
                visualizationData: { equation: `x + ${b} = ${result}` }
            };
        } else {
            return {
                type: 'input',
                question: `<div class="math-expression">${a}x = ${a * x}</div><div>x = ?</div>`,
                correctAnswer: x,
                hint: 'Her iki tarafı da aynı sayıya böl!',
                solution: [
                    `${a}x = ${a * x}`,
                    `x = ${a * x} ÷ ${a}`,
                    `x = ${x}`
                ],
                visualizationType: 'balance',
                visualizationData: { equation: `${a}x = ${a * x}` }
            };
        }
    },

    /**
     * Yüzde hesaplama soruları
     */
    generate_percentage_calculation(difficulty) {
        let base, percentage, result;

        if (difficulty === 'easy') {
            base = Utils.randomInt(10, 100) * 10; // 10'un katları
            percentage = Utils.randomChoice([10, 20, 25, 50, 75]);
        } else {
            base = Utils.randomInt(100, 1000);
            percentage = Utils.randomInt(1, 100);
        }

        result = Math.round((base * percentage) / 100);

        return {
            type: 'input',
            question: `<div>${base} sayısının %${percentage}'i kaçtır?</div>`,
            correctAnswer: result,
            hint: 'Sayıyı 100\'e böl, sonra yüzde ile çarp!',
            solution: [
                `%${percentage} = ${percentage}/100`,
                `${base} × ${percentage}/100 = ${base} × ${percentage / 100}`,
                `= ${result}`
            ],
            visualizationType: 'percentageBar',
            visualizationData: { total: base, percentage: percentage }
        };
    },

    /**
     * Geometri - Alan hesaplama
     */
    generate_area(difficulty) {
        const shapes = ['rectangle', 'square', 'triangle', 'circle'];
        const shape = difficulty === 'easy' ?
            Utils.randomChoice(['rectangle', 'square']) :
            Utils.randomChoice(shapes);

        if (shape === 'rectangle') {
            const width = Utils.randomInt(5, 20);
            const height = Utils.randomInt(5, 20);
            const area = width * height;

            return {
                type: 'input',
                question: `<div>Dikdörtgenin kenarları ${width} cm ve ${height} cm'dir.</div><div>Alanı kaç cm² dir?</div>`,
                correctAnswer: area,
                hint: 'Alan = En × Boy',
                solution: [
                    `Alan = En × Boy`,
                    `Alan = ${width} × ${height}`,
                    `Alan = ${area} cm²`
                ],
                visualizationType: 'rectangle',
                visualizationData: { width, height }
            };
        } else if (shape === 'square') {
            const side = Utils.randomInt(5, 20);
            const area = side * side;

            return {
                type: 'input',
                question: `<div>Karenin bir kenarı ${side} cm'dir.</div><div>Alanı kaç cm²'dir?</div>`,
                correctAnswer: area,
                hint: 'Alan = Kenar × Kenar',
                solution: [
                    `Alan = Kenar²`,
                    `Alan = ${side}²`,
                    `Alan = ${area} cm²`
                ],
                visualizationType: 'square',
                visualizationData: { side }
            };
        } else if (shape === 'triangle') {
            const base = Utils.randomInt(6, 20);
            const height = Utils.randomInt(5, 15);
            const area = (base * height) / 2;

            return {
                type: 'input',
                question: `<div>Üçgenin tabanı ${base} cm, yüksekliği ${height} cm'dir.</div><div>Alanı kaç cm²'dir?</div>`,
                correctAnswer: area,
                hint: 'Alan = (Taban × Yükseklik) ÷ 2',
                solution: [
                    `Alan = (Taban × Yükseklik) ÷ 2`,
                    `Alan = (${base} × ${height}) ÷ 2`,
                    `Alan = ${base * height} ÷ 2`,
                    `Alan = ${area} cm²`
                ],
                visualizationType: 'triangle',
                visualizationData: { base, height }
            };
        } else {
            const radius = Utils.randomInt(5, 15);
            const area = Math.round(Math.PI * radius * radius);

            return {
                type: 'input',
                question: `<div>Dairenin yarıçapı ${radius} cm'dir.</div><div>Alanı yaklaşık kaç cm²'dir? (π ≈ 3.14)</div>`,
                correctAnswer: area,
                hint: 'Alan = π × r²',
                solution: [
                    `Alan = π × r²`,
                    `Alan = 3.14 × ${radius}²`,
                    `Alan = 3.14 × ${radius * radius}`,
                    `Alan ≈ ${area} cm²`
                ],
                visualizationType: 'circle',
                visualizationData: { radius }
            };
        }
    },

    /**
     * Tam sayı işlemleri
     */
    generate_integer_addition(difficulty) {
        let num1, num2;

        if (difficulty === 'easy') {
            num1 = Utils.randomInt(-10, 10);
            num2 = Utils.randomInt(-10, 10);
        } else {
            num1 = Utils.randomInt(-50, 50);
            num2 = Utils.randomInt(-50, 50);
        }

        const result = num1 + num2;

        return {
            type: 'input',
            question: `<div class="math-expression">(${num1}) + (${num2}) = ?</div>`,
            correctAnswer: result,
            hint: 'Pozitif ve negatif işaretleri dikkate al!',
            solution: [
                `(${num1}) + (${num2})`,
                num1 >= 0 && num2 >= 0 ? 'İki pozitif sayı toplanır.' :
                num1 < 0 && num2 < 0 ? 'İki negatif sayı toplanır, sonuç negatif olur.' :
                'Bir pozitif, bir negatif: Büyük olan sayının işareti sonucun işaretidir.',
                `= ${result}`
            ],
            visualizationType: 'numberLine',
            visualizationData: { num1, num2, operation: 'add' }
        };
    },

    /**
     * Üslü sayılar
     */
    generate_power_basics(difficulty) {
        let base, exponent;

        if (difficulty === 'easy') {
            base = Utils.randomInt(2, 5);
            exponent = Utils.randomInt(2, 4);
        } else {
            base = Utils.randomInt(2, 10);
            exponent = Utils.randomInt(2, 5);
        }

        const result = Math.pow(base, exponent);

        return {
            type: 'input',
            question: `<div class="math-expression">${base}<sup>${exponent}</sup> = ?</div>`,
            correctAnswer: result,
            hint: `${base} sayısını ${exponent} defa çarp!`,
            solution: [
                `${base}^${exponent} = ${base} ${'× ' + base + ' '.repeat(exponent - 2)}`,
                `= ${result}`
            ],
            visualizationType: 'power',
            visualizationData: { base, exponent }
        };
    },

    /**
     * İstatistik - Ortalama
     */
    generate_mean(difficulty) {
        let numbers;

        if (difficulty === 'easy') {
            numbers = Array.from({length: 5}, () => Utils.randomInt(1, 20));
        } else {
            numbers = Array.from({length: 8}, () => Utils.randomInt(10, 100));
        }

        const sum = numbers.reduce((a, b) => a + b, 0);
        const mean = Math.round(sum / numbers.length);

        return {
            type: 'input',
            question: `<div>Aşağıdaki sayıların aritmetik ortalaması kaçtır?</div><div class="math-expression">${numbers.join(', ')}</div>`,
            correctAnswer: mean,
            hint: 'Tüm sayıları topla, sayı adedine böl!',
            solution: [
                `Toplam = ${numbers.join(' + ')}`,
                `Toplam = ${sum}`,
                `Ortalama = ${sum} ÷ ${numbers.length}`,
                `Ortalama = ${mean}`
            ],
            visualizationType: 'barChart',
            visualizationData: { numbers }
        };
    },

    /**
     * Ondalık sayı toplama
     */
    generate_decimal_addition(difficulty) {
        let num1, num2;

        if (difficulty === 'easy') {
            num1 = (Utils.randomInt(1, 50) / 10).toFixed(1);
            num2 = (Utils.randomInt(1, 50) / 10).toFixed(1);
        } else {
            num1 = (Utils.randomInt(10, 500) / 100).toFixed(2);
            num2 = (Utils.randomInt(10, 500) / 100).toFixed(2);
        }

        const result = (parseFloat(num1) + parseFloat(num2)).toFixed(difficulty === 'easy' ? 1 : 2);

        return {
            type: 'input',
            question: `<div class="math-expression">${num1} + ${num2} = ?</div>`,
            correctAnswer: parseFloat(result),
            hint: 'Ondalık basamakları hizala!',
            solution: [
                `  ${num1}`,
                `+ ${num2}`,
                `------`,
                `  ${result}`
            ],
            visualizationType: 'decimal',
            visualizationData: { num1: parseFloat(num1), num2: parseFloat(num2) }
        };
    },

    /**
     * Çoktan seçmeli için kesir şıkları üret
     */
    generateFractionOptions(correctNum, correctDen) {
        const options = [`${correctNum}/${correctDen}`];

        // Yanlış şıklar üret
        while (options.length < 4) {
            const wrongNum = correctNum + Utils.randomInt(-3, 3);
            const wrongDen = correctDen + Utils.randomInt(-3, 3);

            if (wrongNum > 0 && wrongDen > 0) {
                const option = `${wrongNum}/${wrongDen}`;
                if (!options.includes(option)) {
                    options.push(option);
                }
            }
        }

        return Utils.shuffle(options);
    },

    /**
     * Varsayılan soru üret
     */
    generateDefaultQuestion(subjectId, topicId, difficulty) {
        const subject = Subjects.getSubjectById(subjectId);
        const topic = Subjects.getTopicById(subjectId, topicId);

        return {
            type: 'multiple-choice',
            question: `<div>${topic.name} konusunda pratik yapıyorsunuz!</div>`,
            correctAnswer: 'A',
            options: ['A', 'B', 'C', 'D'],
            hint: 'Bu bir örnek sorudur.',
            solution: ['Bu konuda soru üreticisi henüz eklenmemiş.'],
            subjectId,
            topicId,
            difficulty
        };
    },

    /**
     * Soru seti üret (birden fazla soru)
     */
    generateQuestionSet(subjectId, topicId, difficulty, count = 10) {
        const questions = [];

        for (let i = 0; i < count; i++) {
            questions.push(this.generate(subjectId, topicId, difficulty));
        }

        return questions;
    },

    /**
     * Günlük meydan okuma soruları üret
     */
    generateDailyChallenge() {
        const questions = [];
        const difficulties = ['easy', 'easy', 'medium', 'medium', 'hard'];

        difficulties.forEach(difficulty => {
            const randomSubject = Subjects.getRandomSubject();
            const randomTopic = Subjects.getRandomTopic(randomSubject.id, difficulty);

            if (randomTopic) {
                questions.push(this.generate(randomSubject.id, randomTopic.id, difficulty));
            }
        });

        return questions;
    },

    /**
     * Cevabı kontrol et
     */
    checkAnswer(question, userAnswer) {
        const correctAnswer = question.correctAnswer.toString().toLowerCase();
        const answer = userAnswer.toString().toLowerCase().trim();

        // Sayısal cevaplar için tolerans
        if (question.type === 'input' && !isNaN(correctAnswer) && !isNaN(answer)) {
            const correct = parseFloat(correctAnswer);
            const user = parseFloat(answer);
            return Math.abs(correct - user) < 0.01; // Küçük tolerans
        }

        return correctAnswer === answer;
    }
};

// Global erişim için
window.QuestionGenerator = QuestionGenerator;
