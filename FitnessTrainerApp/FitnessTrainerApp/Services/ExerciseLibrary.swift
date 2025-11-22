import Foundation

class ExerciseLibrary {
    static let shared = ExerciseLibrary()

    private init() {}

    func getAllExercises() -> [Exercise] {
        return [
            // GÖĞÜS EGZERSİZLERİ
            Exercise(
                name: "Barbell Bench Press",
                muscleGroup: .chest,
                difficulty: .intermediate,
                description: "Klasik göğüs geliştirme hareketi",
                instructions: [
                    "Düz benche sırt üstü uzanın",
                    "Barı omuz genişliğinden biraz daha geniş tutun",
                    "Barı göğsünüze doğru indirin",
                    "Kontrollü şekilde yukarı itin"
                ],
                imageURL: "figure.strengthtraining.traditional"
            ),
            Exercise(
                name: "Push-Up",
                muscleGroup: .chest,
                difficulty: .beginner,
                description: "Vücut ağırlığıyla yapılan temel göğüs hareketi",
                instructions: [
                    "Plank pozisyonunda durun",
                    "Eller omuz hizasında",
                    "Gövdeyi düz tutarak aşağı inin",
                    "Yukarı itin ve başlangıç pozisyonuna dönün"
                ],
                imageURL: "figure.mind.and.body"
            ),
            Exercise(
                name: "Dumbbell Flyes",
                muscleGroup: .chest,
                difficulty: .intermediate,
                description: "Göğüs kaslarını izole eden hareket",
                instructions: [
                    "Düz benche sırt üstü uzanın",
                    "Dumbbellları yukarıda tutun",
                    "Dirsekleri hafif bükerek yanlara açın",
                    "Göğüs kaslarınızı sıkarak geri getirin"
                ],
                imageURL: "figure.strengthtraining.traditional"
            ),

            // SIRT EGZERSİZLERİ
            Exercise(
                name: "Pull-Up",
                muscleGroup: .back,
                difficulty: .advanced,
                description: "Sırt ve kol geliştiren üst vücut hareketi",
                instructions: [
                    "Barı omuz genişliğinde tutun",
                    "Kendinizi yukarı çekin",
                    "Çene bar seviyesine gelene kadar çekin",
                    "Kontrollü şekilde aşağı inin"
                ],
                imageURL: "figure.climbing"
            ),
            Exercise(
                name: "Barbell Row",
                muscleGroup: .back,
                difficulty: .intermediate,
                description: "Sırt kalınlığı geliştiren hareket",
                instructions: [
                    "Ayaklar omuz genişliğinde",
                    "Öne eğilin, sırt düz",
                    "Barı göbeğe doğru çekin",
                    "Kürek kemiklerini sıkıştırın"
                ],
                imageURL: "figure.strengthtraining.traditional"
            ),
            Exercise(
                name: "Lat Pulldown",
                muscleGroup: .back,
                difficulty: .beginner,
                description: "Sırt genişliği geliştiren hareket",
                instructions: [
                    "Lat pulldown makinesine oturun",
                    "Barı geniş tutun",
                    "Göğse doğru çekin",
                    "Kontrollü şekilde geri bırakın"
                ],
                imageURL: "figure.strengthtraining.traditional"
            ),

            // OMUZ EGZERSİZLERİ
            Exercise(
                name: "Overhead Press",
                muscleGroup: .shoulders,
                difficulty: .intermediate,
                description: "Omuz güçlendirme hareketi",
                instructions: [
                    "Ayakta durun, bar omuz hizasında",
                    "Barı yukarı itin",
                    "Kollar tamamen düzelene kadar itin",
                    "Kontrollü şekilde indirin"
                ],
                imageURL: "figure.strengthtraining.traditional"
            ),
            Exercise(
                name: "Lateral Raises",
                muscleGroup: .shoulders,
                difficulty: .beginner,
                description: "Yan omuz geliştirme",
                instructions: [
                    "Ayakta durun, dumbbelllar yanınızda",
                    "Kolları yanlara kaldırın",
                    "Omuz hizasına kadar yükseltin",
                    "Kontrollü şekilde indirin"
                ],
                imageURL: "figure.arms.open"
            ),

            // BİCEPS EGZERSİZLERİ
            Exercise(
                name: "Barbell Curl",
                muscleGroup: .biceps,
                difficulty: .beginner,
                description: "Klasik biceps hareketi",
                instructions: [
                    "Ayakta durun, bar elde",
                    "Dirsekler sabit, barı yukarı kaldırın",
                    "Bicepsleri tam olarak kasın",
                    "Kontrollü şekilde indirin"
                ],
                imageURL: "figure.strengthtraining.traditional"
            ),
            Exercise(
                name: "Hammer Curl",
                muscleGroup: .biceps,
                difficulty: .beginner,
                description: "Biceps ve önkol geliştirme",
                instructions: [
                    "Dumbbellları neutral grip ile tutun",
                    "Dirsekler sabit",
                    "Yukarı kaldırın",
                    "Kontrollü şekilde indirin"
                ],
                imageURL: "figure.strengthtraining.traditional"
            ),

            // TRİCEPS EGZERSİZLERİ
            Exercise(
                name: "Triceps Dips",
                muscleGroup: .triceps,
                difficulty: .intermediate,
                description: "Vücut ağırlığıyla triceps geliştirme",
                instructions: [
                    "Paralel barlara tutunun",
                    "Vücudu aşağı indirin",
                    "Dirsekler 90 derece olana kadar",
                    "Yukarı itin"
                ],
                imageURL: "figure.strengthtraining.traditional"
            ),
            Exercise(
                name: "Overhead Triceps Extension",
                muscleGroup: .triceps,
                difficulty: .beginner,
                description: "Triceps izolasyon hareketi",
                instructions: [
                    "Dumbbell'ı başın üstünde tutun",
                    "Dirseği bükerek arkaya indirin",
                    "Tricepsi kasarak yukarı itin",
                    "Dirsek sabit kalmalı"
                ],
                imageURL: "figure.strengthtraining.traditional"
            ),

            // BACAK EGZERSİZLERİ
            Exercise(
                name: "Barbell Squat",
                muscleGroup: .legs,
                difficulty: .intermediate,
                description: "Bacak geliştirmenin kralı",
                instructions: [
                    "Bar omuzlarda",
                    "Ayaklar omuz genişliğinde",
                    "Kalça arkaya giderek çömelin",
                    "Topukları iterek kalkın"
                ],
                imageURL: "figure.strengthtraining.traditional"
            ),
            Exercise(
                name: "Lunges",
                muscleGroup: .legs,
                difficulty: .beginner,
                description: "Bacak ve denge geliştirme",
                instructions: [
                    "Ayakta durun",
                    "Bir adım öne atın",
                    "Ön diz 90 derece olana kadar inin",
                    "Başlangıç pozisyonuna dönün"
                ],
                imageURL: "figure.walk"
            ),
            Exercise(
                name: "Romanian Deadlift",
                muscleGroup: .legs,
                difficulty: .intermediate,
                description: "Arka bacak ve sırt alt geliştirme",
                instructions: [
                    "Bar elde, ayaklar omuz genişliğinde",
                    "Sırt düz, öne eğilin",
                    "Bar bacak önünden aşağı insin",
                    "Kalçayı sıkarak yukarı kalkın"
                ],
                imageURL: "figure.strengthtraining.traditional"
            ),

            // KARIN EGZERSİZLERİ
            Exercise(
                name: "Plank",
                muscleGroup: .abs,
                difficulty: .beginner,
                description: "Core stabilizasyon hareketi",
                instructions: [
                    "Dirsekler üzerinde plank pozisyonu",
                    "Vücut düz bir çizgi",
                    "Pozisyonu koruyun",
                    "Düzenli nefes alın"
                ],
                imageURL: "figure.core.training"
            ),
            Exercise(
                name: "Crunches",
                muscleGroup: .abs,
                difficulty: .beginner,
                description: "Üst karın geliştirme",
                instructions: [
                    "Sırt üstü uzanın, dizler bükük",
                    "Eller kulak hizasında",
                    "Omuzları yerden kaldırın",
                    "Karın kaslarını sıkın"
                ],
                imageURL: "figure.core.training"
            ),
            Exercise(
                name: "Russian Twist",
                muscleGroup: .abs,
                difficulty: .intermediate,
                description: "Yan karın ve core geliştirme",
                instructions: [
                    "Oturur pozisyonda, ayaklar havada",
                    "Gövdeyi sağa sola döndürün",
                    "Ağırlık varsa yan yana dokundurün",
                    "Kontrollü hareket edin"
                ],
                imageURL: "figure.core.training"
            ),

            // KARDİYO
            Exercise(
                name: "Running",
                muscleGroup: .cardio,
                difficulty: .beginner,
                description: "Kardiyo dayanıklılık",
                instructions: [
                    "Tempolu koşu",
                    "Düzenli nefes",
                    "20-30 dakika",
                    "Orta tempo"
                ],
                imageURL: "figure.run"
            ),
            Exercise(
                name: "Jumping Jacks",
                muscleGroup: .cardio,
                difficulty: .beginner,
                description: "Isınma ve kardiyo",
                instructions: [
                    "Ayakta durun",
                    "Zıplayarak bacakları aç",
                    "Kolları yukarı kaldır",
                    "Başlangıç pozisyonuna dön"
                ],
                imageURL: "figure.jumprope"
            )
        ]
    }

    func getExercises(for muscleGroup: MuscleGroup) -> [Exercise] {
        return getAllExercises().filter { $0.muscleGroup == muscleGroup }
    }

    func getExercises(for difficulty: ExerciseDifficulty) -> [Exercise] {
        return getAllExercises().filter { $0.difficulty == difficulty }
    }
}
