import Foundation

enum BodyType: String, Codable, CaseIterable {
    case ectomorph = "Ektomorf"      // İnce, hızlı metabolizma
    case mesomorph = "Mezomorf"      // Atletik, kas yapmaya yatkın
    case endomorph = "Endomorf"      // Güçlü, yağ yapmaya yatkın

    var description: String {
        switch self {
        case .ectomorph:
            return "İnce yapılı, hızlı metabolizma, kas yapmakta zorlanır"
        case .mesomorph:
            return "Atletik yapı, kas yapmaya yatkın, dengeli metabolizma"
        case .endomorph:
            return "Güçlü yapı, kuvvetli, yağ yapmaya yatkın"
        }
    }
}

enum FitnessGoal: String, Codable, CaseIterable {
    case loseWeight = "Kilo Vermek"
    case gainMuscle = "Kas Yapmak"
    case getStronger = "Güçlenmek"
    case stayFit = "Fit Kalmak"
}

struct UserProfile: Codable, Identifiable {
    let id: UUID
    var name: String
    var bodyType: BodyType
    var currentWeight: Double
    var targetWeight: Double
    var goal: FitnessGoal
    var height: Double
    var age: Int
    var gender: String
    var createdDate: Date

    init(id: UUID = UUID(), name: String, bodyType: BodyType, currentWeight: Double,
         targetWeight: Double, goal: FitnessGoal, height: Double, age: Int, gender: String) {
        self.id = id
        self.name = name
        self.bodyType = bodyType
        self.currentWeight = currentWeight
        self.targetWeight = targetWeight
        self.goal = goal
        self.height = height
        self.age = age
        self.gender = gender
        self.createdDate = Date()
    }
}
