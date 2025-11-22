import Foundation

struct WeightRecord: Codable, Identifiable {
    let id: UUID
    let date: Date
    let weight: Double
    let notes: String?

    init(id: UUID = UUID(), date: Date = Date(), weight: Double, notes: String? = nil) {
        self.id = id
        self.date = date
        self.weight = weight
        self.notes = notes
    }
}

struct WorkoutSession: Codable, Identifiable {
    let id: UUID
    let workoutDayId: UUID
    let date: Date
    var completedExercises: [CompletedExercise]
    var duration: TimeInterval
    var notes: String?

    init(id: UUID = UUID(), workoutDayId: UUID, date: Date = Date(),
         completedExercises: [CompletedExercise], duration: TimeInterval, notes: String? = nil) {
        self.id = id
        self.workoutDayId = workoutDayId
        self.date = date
        self.completedExercises = completedExercises
        self.duration = duration
        self.notes = notes
    }
}

struct CompletedExercise: Codable, Identifiable {
    let id: UUID
    let exerciseId: UUID
    let exerciseName: String
    var completedSets: [CompletedSet]

    init(id: UUID = UUID(), exerciseId: UUID, exerciseName: String, completedSets: [CompletedSet]) {
        self.id = id
        self.exerciseId = exerciseId
        self.exerciseName = exerciseName
        self.completedSets = completedSets
    }
}

struct CompletedSet: Codable, Identifiable {
    let id: UUID
    let reps: Int
    let weight: Double
    let completedDate: Date

    init(id: UUID = UUID(), reps: Int, weight: Double, completedDate: Date = Date()) {
        self.id = id
        self.reps = reps
        self.weight = weight
        self.completedDate = completedDate
    }
}
