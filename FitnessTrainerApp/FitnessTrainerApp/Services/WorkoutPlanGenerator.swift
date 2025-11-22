import Foundation

class WorkoutPlanGenerator {
    static let shared = WorkoutPlanGenerator()
    private let exerciseLibrary = ExerciseLibrary.shared

    private init() {}

    func generatePlan(for profile: UserProfile) -> WorkoutPlan {
        let exercises = exerciseLibrary.getAllExercises()

        switch (profile.bodyType, profile.goal) {
        case (.ectomorph, .gainMuscle):
            return createEctomorphMusclePlan(exercises: exercises)
        case (.ectomorph, .getStronger):
            return createStrengthPlan(exercises: exercises)
        case (.mesomorph, .gainMuscle):
            return createMesomorphMusclePlan(exercises: exercises)
        case (.mesomorph, .loseWeight):
            return createMesomorphCuttingPlan(exercises: exercises)
        case (.endomorph, .loseWeight):
            return createEndomorphWeightLossPlan(exercises: exercises)
        case (.endomorph, .getStronger):
            return createStrengthPlan(exercises: exercises)
        default:
            return createBalancedPlan(exercises: exercises)
        }
    }

    // EKTOMORF - KAS YAPMA PLANI
    private func createEctomorphMusclePlan(exercises: [Exercise]) -> WorkoutPlan {
        let workoutDays = [
            // Pazartesi - Göğüs ve Triceps
            WorkoutDay(
                day: .monday,
                muscleGroups: [.chest, .triceps],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Barbell Bench Press", in: exercises)!, sets: 4, reps: 8, restSeconds: 90),
                    WorkoutExercise(exercise: findExercise("Push-Up", in: exercises)!, sets: 3, reps: 12, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Dumbbell Flyes", in: exercises)!, sets: 3, reps: 10, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Triceps Dips", in: exercises)!, sets: 3, reps: 10, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Overhead Triceps Extension", in: exercises)!, sets: 3, reps: 12, restSeconds: 60)
                ]
            ),
            // Çarşamba - Sırt ve Biceps
            WorkoutDay(
                day: .wednesday,
                muscleGroups: [.back, .biceps],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Barbell Row", in: exercises)!, sets: 4, reps: 8, restSeconds: 90),
                    WorkoutExercise(exercise: findExercise("Lat Pulldown", in: exercises)!, sets: 3, reps: 10, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Pull-Up", in: exercises)!, sets: 3, reps: 8, restSeconds: 90),
                    WorkoutExercise(exercise: findExercise("Barbell Curl", in: exercises)!, sets: 3, reps: 10, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Hammer Curl", in: exercises)!, sets: 3, reps: 12, restSeconds: 60)
                ]
            ),
            // Cuma - Bacak ve Omuz
            WorkoutDay(
                day: .friday,
                muscleGroups: [.legs, .shoulders],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Barbell Squat", in: exercises)!, sets: 4, reps: 8, restSeconds: 120),
                    WorkoutExercise(exercise: findExercise("Romanian Deadlift", in: exercises)!, sets: 3, reps: 10, restSeconds: 90),
                    WorkoutExercise(exercise: findExercise("Lunges", in: exercises)!, sets: 3, reps: 12, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Overhead Press", in: exercises)!, sets: 4, reps: 8, restSeconds: 90),
                    WorkoutExercise(exercise: findExercise("Lateral Raises", in: exercises)!, sets: 3, reps: 12, restSeconds: 60)
                ]
            )
        ]

        return WorkoutPlan(
            name: "Ektomorf Kas Yapma Programı",
            bodyType: .ectomorph,
            goal: .gainMuscle,
            workoutDays: workoutDays
        )
    }

    // MEZOMORF - KAS YAPMA PLANI
    private func createMesomorphMusclePlan(exercises: [Exercise]) -> WorkoutPlan {
        let workoutDays = [
            // Pazartesi - Göğüs
            WorkoutDay(
                day: .monday,
                muscleGroups: [.chest],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Barbell Bench Press", in: exercises)!, sets: 4, reps: 10, restSeconds: 90),
                    WorkoutExercise(exercise: findExercise("Dumbbell Flyes", in: exercises)!, sets: 4, reps: 12, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Push-Up", in: exercises)!, sets: 3, reps: 15, restSeconds: 45)
                ]
            ),
            // Salı - Sırt
            WorkoutDay(
                day: .tuesday,
                muscleGroups: [.back],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Pull-Up", in: exercises)!, sets: 4, reps: 10, restSeconds: 90),
                    WorkoutExercise(exercise: findExercise("Barbell Row", in: exercises)!, sets: 4, reps: 10, restSeconds: 90),
                    WorkoutExercise(exercise: findExercise("Lat Pulldown", in: exercises)!, sets: 3, reps: 12, restSeconds: 60)
                ]
            ),
            // Perşembe - Omuz ve Karın
            WorkoutDay(
                day: .thursday,
                muscleGroups: [.shoulders, .abs],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Overhead Press", in: exercises)!, sets: 4, reps: 10, restSeconds: 90),
                    WorkoutExercise(exercise: findExercise("Lateral Raises", in: exercises)!, sets: 4, reps: 12, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Plank", in: exercises)!, sets: 3, reps: 60, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Russian Twist", in: exercises)!, sets: 3, reps: 20, restSeconds: 45)
                ]
            ),
            // Cuma - Kol (Biceps ve Triceps)
            WorkoutDay(
                day: .friday,
                muscleGroups: [.biceps, .triceps],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Barbell Curl", in: exercises)!, sets: 4, reps: 10, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Hammer Curl", in: exercises)!, sets: 3, reps: 12, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Triceps Dips", in: exercises)!, sets: 4, reps: 10, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Overhead Triceps Extension", in: exercises)!, sets: 3, reps: 12, restSeconds: 60)
                ]
            ),
            // Cumartesi - Bacak
            WorkoutDay(
                day: .saturday,
                muscleGroups: [.legs],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Barbell Squat", in: exercises)!, sets: 4, reps: 10, restSeconds: 120),
                    WorkoutExercise(exercise: findExercise("Romanian Deadlift", in: exercises)!, sets: 4, reps: 10, restSeconds: 90),
                    WorkoutExercise(exercise: findExercise("Lunges", in: exercises)!, sets: 3, reps: 12, restSeconds: 60)
                ]
            )
        ]

        return WorkoutPlan(
            name: "Mezomorf Kas Geliştirme Programı",
            bodyType: .mesomorph,
            goal: .gainMuscle,
            workoutDays: workoutDays
        )
    }

    // ENDOMORF - KİLO VERME PLANI
    private func createEndomorphWeightLossPlan(exercises: [Exercise]) -> WorkoutPlan {
        let workoutDays = [
            // Pazartesi - Full Body + Kardiyo
            WorkoutDay(
                day: .monday,
                muscleGroups: [.chest, .back, .cardio],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Push-Up", in: exercises)!, sets: 4, reps: 15, restSeconds: 45),
                    WorkoutExercise(exercise: findExercise("Lat Pulldown", in: exercises)!, sets: 4, reps: 12, restSeconds: 45),
                    WorkoutExercise(exercise: findExercise("Jumping Jacks", in: exercises)!, sets: 3, reps: 30, restSeconds: 30),
                    WorkoutExercise(exercise: findExercise("Running", in: exercises)!, sets: 1, reps: 20, restSeconds: 0, notes: "20 dakika orta tempo koşu")
                ]
            ),
            // Çarşamba - Alt Vücut + Kardiyo
            WorkoutDay(
                day: .wednesday,
                muscleGroups: [.legs, .abs, .cardio],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Barbell Squat", in: exercises)!, sets: 4, reps: 15, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Lunges", in: exercises)!, sets: 4, reps: 15, restSeconds: 45),
                    WorkoutExercise(exercise: findExercise("Plank", in: exercises)!, sets: 3, reps: 60, restSeconds: 45),
                    WorkoutExercise(exercise: findExercise("Crunches", in: exercises)!, sets: 3, reps: 20, restSeconds: 30),
                    WorkoutExercise(exercise: findExercise("Running", in: exercises)!, sets: 1, reps: 25, restSeconds: 0, notes: "25 dakika koşu")
                ]
            ),
            // Cuma - Üst Vücut + Kardiyo
            WorkoutDay(
                day: .friday,
                muscleGroups: [.shoulders, .biceps, .triceps, .cardio],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Overhead Press", in: exercises)!, sets: 4, reps: 12, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Lateral Raises", in: exercises)!, sets: 3, reps: 15, restSeconds: 45),
                    WorkoutExercise(exercise: findExercise("Barbell Curl", in: exercises)!, sets: 3, reps: 12, restSeconds: 45),
                    WorkoutExercise(exercise: findExercise("Triceps Dips", in: exercises)!, sets: 3, reps: 12, restSeconds: 45),
                    WorkoutExercise(exercise: findExercise("Jumping Jacks", in: exercises)!, sets: 4, reps: 30, restSeconds: 30)
                ]
            ),
            // Cumartesi - Kardiyo ve Core
            WorkoutDay(
                day: .saturday,
                muscleGroups: [.cardio, .abs],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Running", in: exercises)!, sets: 1, reps: 30, restSeconds: 0, notes: "30 dakika koşu"),
                    WorkoutExercise(exercise: findExercise("Plank", in: exercises)!, sets: 4, reps: 60, restSeconds: 45),
                    WorkoutExercise(exercise: findExercise("Russian Twist", in: exercises)!, sets: 4, reps: 25, restSeconds: 30),
                    WorkoutExercise(exercise: findExercise("Crunches", in: exercises)!, sets: 4, reps: 20, restSeconds: 30)
                ]
            )
        ]

        return WorkoutPlan(
            name: "Endomorf Yağ Yakma Programı",
            bodyType: .endomorph,
            goal: .loseWeight,
            workoutDays: workoutDays
        )
    }

    // MEZOMORF - KİLO VERME (CUTTING)
    private func createMesomorphCuttingPlan(exercises: [Exercise]) -> WorkoutPlan {
        let workoutDays = [
            WorkoutDay(
                day: .monday,
                muscleGroups: [.chest, .triceps, .cardio],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Barbell Bench Press", in: exercises)!, sets: 4, reps: 12, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Push-Up", in: exercises)!, sets: 3, reps: 15, restSeconds: 45),
                    WorkoutExercise(exercise: findExercise("Triceps Dips", in: exercises)!, sets: 3, reps: 12, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Jumping Jacks", in: exercises)!, sets: 3, reps: 30, restSeconds: 30)
                ]
            ),
            WorkoutDay(
                day: .wednesday,
                muscleGroups: [.back, .biceps, .cardio],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Pull-Up", in: exercises)!, sets: 4, reps: 10, restSeconds: 90),
                    WorkoutExercise(exercise: findExercise("Barbell Row", in: exercises)!, sets: 4, reps: 12, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Barbell Curl", in: exercises)!, sets: 3, reps: 12, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Running", in: exercises)!, sets: 1, reps: 20, restSeconds: 0)
                ]
            ),
            WorkoutDay(
                day: .friday,
                muscleGroups: [.legs, .abs, .cardio],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Barbell Squat", in: exercises)!, sets: 4, reps: 15, restSeconds: 90),
                    WorkoutExercise(exercise: findExercise("Lunges", in: exercises)!, sets: 4, reps: 15, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Plank", in: exercises)!, sets: 3, reps: 60, restSeconds: 45),
                    WorkoutExercise(exercise: findExercise("Russian Twist", in: exercises)!, sets: 3, reps: 20, restSeconds: 45)
                ]
            )
        ]

        return WorkoutPlan(
            name: "Mezomorf Definasyon Programı",
            bodyType: .mesomorph,
            goal: .loseWeight,
            workoutDays: workoutDays
        )
    }

    // KUVVET PROGRAMI (Tüm vücut tipleri için)
    private func createStrengthPlan(exercises: [Exercise]) -> WorkoutPlan {
        let workoutDays = [
            WorkoutDay(
                day: .monday,
                muscleGroups: [.chest, .triceps],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Barbell Bench Press", in: exercises)!, sets: 5, reps: 5, restSeconds: 180),
                    WorkoutExercise(exercise: findExercise("Dumbbell Flyes", in: exercises)!, sets: 3, reps: 8, restSeconds: 90),
                    WorkoutExercise(exercise: findExercise("Triceps Dips", in: exercises)!, sets: 4, reps: 6, restSeconds: 120)
                ]
            ),
            WorkoutDay(
                day: .wednesday,
                muscleGroups: [.legs],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Barbell Squat", in: exercises)!, sets: 5, reps: 5, restSeconds: 180),
                    WorkoutExercise(exercise: findExercise("Romanian Deadlift", in: exercises)!, sets: 4, reps: 6, restSeconds: 150),
                    WorkoutExercise(exercise: findExercise("Lunges", in: exercises)!, sets: 3, reps: 8, restSeconds: 90)
                ]
            ),
            WorkoutDay(
                day: .friday,
                muscleGroups: [.back, .biceps],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Pull-Up", in: exercises)!, sets: 5, reps: 5, restSeconds: 180),
                    WorkoutExercise(exercise: findExercise("Barbell Row", in: exercises)!, sets: 5, reps: 5, restSeconds: 180),
                    WorkoutExercise(exercise: findExercise("Barbell Curl", in: exercises)!, sets: 3, reps: 8, restSeconds: 90)
                ]
            )
        ]

        return WorkoutPlan(
            name: "Kuvvet Geliştirme Programı",
            bodyType: .mesomorph,
            goal: .getStronger,
            workoutDays: workoutDays
        )
    }

    // DENGELİ PROGRAM
    private func createBalancedPlan(exercises: [Exercise]) -> WorkoutPlan {
        let workoutDays = [
            WorkoutDay(
                day: .monday,
                muscleGroups: [.chest, .triceps],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Barbell Bench Press", in: exercises)!, sets: 3, reps: 10, restSeconds: 90),
                    WorkoutExercise(exercise: findExercise("Push-Up", in: exercises)!, sets: 3, reps: 12, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Triceps Dips", in: exercises)!, sets: 3, reps: 10, restSeconds: 60)
                ]
            ),
            WorkoutDay(
                day: .wednesday,
                muscleGroups: [.back, .biceps],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Lat Pulldown", in: exercises)!, sets: 3, reps: 10, restSeconds: 90),
                    WorkoutExercise(exercise: findExercise("Barbell Row", in: exercises)!, sets: 3, reps: 10, restSeconds: 90),
                    WorkoutExercise(exercise: findExercise("Barbell Curl", in: exercises)!, sets: 3, reps: 12, restSeconds: 60)
                ]
            ),
            WorkoutDay(
                day: .friday,
                muscleGroups: [.legs, .shoulders],
                exercises: [
                    WorkoutExercise(exercise: findExercise("Barbell Squat", in: exercises)!, sets: 3, reps: 10, restSeconds: 120),
                    WorkoutExercise(exercise: findExercise("Lunges", in: exercises)!, sets: 3, reps: 12, restSeconds: 60),
                    WorkoutExercise(exercise: findExercise("Overhead Press", in: exercises)!, sets: 3, reps: 10, restSeconds: 90)
                ]
            )
        ]

        return WorkoutPlan(
            name: "Dengeli Fitness Programı",
            bodyType: .mesomorph,
            goal: .stayFit,
            workoutDays: workoutDays
        )
    }

    private func findExercise(_ name: String, in exercises: [Exercise]) -> Exercise? {
        return exercises.first { $0.name == name }
    }
}
