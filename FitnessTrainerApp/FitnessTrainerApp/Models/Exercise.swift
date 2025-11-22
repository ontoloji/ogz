import Foundation

enum MuscleGroup: String, Codable, CaseIterable {
    case chest = "Göğüs"
    case back = "Sırt"
    case shoulders = "Omuz"
    case biceps = "Biceps"
    case triceps = "Triceps"
    case legs = "Bacak"
    case abs = "Karın"
    case cardio = "Kardiyo"
}

enum ExerciseDifficulty: String, Codable {
    case beginner = "Başlangıç"
    case intermediate = "Orta"
    case advanced = "İleri"
}

struct Exercise: Codable, Identifiable {
    let id: UUID
    let name: String
    let muscleGroup: MuscleGroup
    let difficulty: ExerciseDifficulty
    let description: String
    let instructions: [String]
    let imageURL: String  // SF Symbol veya asset adı
    let videoURL: String?

    init(id: UUID = UUID(), name: String, muscleGroup: MuscleGroup,
         difficulty: ExerciseDifficulty, description: String,
         instructions: [String], imageURL: String, videoURL: String? = nil) {
        self.id = id
        self.name = name
        self.muscleGroup = muscleGroup
        self.difficulty = difficulty
        self.description = description
        self.instructions = instructions
        self.imageURL = imageURL
        self.videoURL = videoURL
    }
}

struct ExerciseSet: Codable, Identifiable {
    let id: UUID
    let exerciseId: UUID
    var reps: Int
    var weight: Double
    var isCompleted: Bool
    var completedDate: Date?

    init(id: UUID = UUID(), exerciseId: UUID, reps: Int, weight: Double, isCompleted: Bool = false) {
        self.id = id
        self.exerciseId = exerciseId
        self.reps = reps
        self.weight = weight
        self.isCompleted = isCompleted
        self.completedDate = nil
    }
}
