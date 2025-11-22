import Foundation
import Combine

class DataManager: ObservableObject {
    @Published var userProfile: UserProfile?
    @Published var currentWorkoutPlan: WorkoutPlan?
    @Published var weightRecords: [WeightRecord] = []
    @Published var workoutSessions: [WorkoutSession] = []

    private let userDefaults = UserDefaults.standard
    private let profileKey = "userProfile"
    private let planKey = "workoutPlan"
    private let weightKey = "weightRecords"
    private let sessionsKey = "workoutSessions"

    init() {
        loadData()
    }

    // MARK: - Profile Management
    func saveProfile(_ profile: UserProfile) {
        self.userProfile = profile
        if let encoded = try? JSONEncoder().encode(profile) {
            userDefaults.set(encoded, forKey: profileKey)
        }
        // Profil kaydedildiğinde otomatik plan oluştur
        generateWorkoutPlan()
    }

    func generateWorkoutPlan() {
        guard let profile = userProfile else { return }
        let plan = WorkoutPlanGenerator.shared.generatePlan(for: profile)
        self.currentWorkoutPlan = plan
        if let encoded = try? JSONEncoder().encode(plan) {
            userDefaults.set(encoded, forKey: planKey)
        }
    }

    // MARK: - Weight Tracking
    func addWeightRecord(_ record: WeightRecord) {
        weightRecords.insert(record, at: 0)
        saveWeightRecords()

        // Kullanıcı profilindeki mevcut kiloyu güncelle
        if var profile = userProfile {
            profile.currentWeight = record.weight
            saveProfile(profile)
        }
    }

    func deleteWeightRecord(_ record: WeightRecord) {
        weightRecords.removeAll { $0.id == record.id }
        saveWeightRecords()
    }

    private func saveWeightRecords() {
        if let encoded = try? JSONEncoder().encode(weightRecords) {
            userDefaults.set(encoded, forKey: weightKey)
        }
    }

    // MARK: - Workout Session Tracking
    func saveWorkoutSession(_ session: WorkoutSession) {
        workoutSessions.insert(session, at: 0)
        saveWorkoutSessions()
    }

    func deleteWorkoutSession(_ session: WorkoutSession) {
        workoutSessions.removeAll { $0.id == session.id }
        saveWorkoutSessions()
    }

    private func saveWorkoutSessions() {
        if let encoded = try? JSONEncoder().encode(workoutSessions) {
            userDefaults.set(encoded, forKey: sessionsKey)
        }
    }

    // MARK: - Statistics
    func getWeightProgress() -> (current: Double, target: Double, change: Double)? {
        guard let profile = userProfile else { return nil }
        let change = profile.currentWeight - (weightRecords.last?.weight ?? profile.currentWeight)
        return (profile.currentWeight, profile.targetWeight, change)
    }

    func getTotalWorkouts() -> Int {
        return workoutSessions.count
    }

    func getWorkoutsThisWeek() -> Int {
        let calendar = Calendar.current
        let weekAgo = calendar.date(byAdding: .day, value: -7, to: Date())!
        return workoutSessions.filter { $0.date >= weekAgo }.count
    }

    func getAverageWorkoutDuration() -> TimeInterval {
        guard !workoutSessions.isEmpty else { return 0 }
        let total = workoutSessions.reduce(0.0) { $0 + $1.duration }
        return total / Double(workoutSessions.count)
    }

    // MARK: - Data Persistence
    private func loadData() {
        // Load profile
        if let data = userDefaults.data(forKey: profileKey),
           let profile = try? JSONDecoder().decode(UserProfile.self, from: data) {
            self.userProfile = profile
        }

        // Load workout plan
        if let data = userDefaults.data(forKey: planKey),
           let plan = try? JSONDecoder().decode(WorkoutPlan.self, from: data) {
            self.currentWorkoutPlan = plan
        }

        // Load weight records
        if let data = userDefaults.data(forKey: weightKey),
           let records = try? JSONDecoder().decode([WeightRecord].self, from: data) {
            self.weightRecords = records
        }

        // Load workout sessions
        if let data = userDefaults.data(forKey: sessionsKey),
           let sessions = try? JSONDecoder().decode([WorkoutSession].self, from: data) {
            self.workoutSessions = sessions
        }
    }

    func clearAllData() {
        userProfile = nil
        currentWorkoutPlan = nil
        weightRecords = []
        workoutSessions = []

        userDefaults.removeObject(forKey: profileKey)
        userDefaults.removeObject(forKey: planKey)
        userDefaults.removeObject(forKey: weightKey)
        userDefaults.removeObject(forKey: sessionsKey)
    }
}
