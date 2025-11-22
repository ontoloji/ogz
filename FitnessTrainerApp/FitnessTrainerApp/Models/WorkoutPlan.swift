import Foundation

enum WeekDay: String, Codable, CaseIterable {
    case monday = "Pazartesi"
    case tuesday = "Salı"
    case wednesday = "Çarşamba"
    case thursday = "Perşembe"
    case friday = "Cuma"
    case saturday = "Cumartesi"
    case sunday = "Pazar"
}

struct WorkoutDay: Codable, Identifiable {
    let id: UUID
    let day: WeekDay
    let muscleGroups: [MuscleGroup]
    var exercises: [WorkoutExercise]

    init(id: UUID = UUID(), day: WeekDay, muscleGroups: [MuscleGroup], exercises: [WorkoutExercise]) {
        self.id = id
        self.day = day
        self.muscleGroups = muscleGroups
        self.exercises = exercises
    }
}

struct WorkoutExercise: Codable, Identifiable {
    let id: UUID
    let exercise: Exercise
    var sets: Int
    var reps: Int
    var restSeconds: Int
    var notes: String?

    init(id: UUID = UUID(), exercise: Exercise, sets: Int, reps: Int, restSeconds: Int = 60, notes: String? = nil) {
        self.id = id
        self.exercise = exercise
        self.sets = sets
        self.reps = reps
        self.restSeconds = restSeconds
        self.notes = notes
    }
}

struct WorkoutPlan: Codable, Identifiable {
    let id: UUID
    let name: String
    let bodyType: BodyType
    let goal: FitnessGoal
    var workoutDays: [WorkoutDay]
    let createdDate: Date

    init(id: UUID = UUID(), name: String, bodyType: BodyType, goal: FitnessGoal, workoutDays: [WorkoutDay]) {
        self.id = id
        self.name = name
        self.bodyType = bodyType
        self.goal = goal
        self.workoutDays = workoutDays
        self.createdDate = Date()
    }
}
