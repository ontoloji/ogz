import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var dataManager: DataManager
    @State private var showingResetAlert = false
    @State private var showingProfileEdit = false

    var body: some View {
        NavigationView {
            List {
                // Profile Section
                Section("Profil") {
                    if let profile = dataManager.userProfile {
                        ProfileInfoRow(icon: "person.fill", title: "İsim", value: profile.name)
                        ProfileInfoRow(icon: "calendar", title: "Yaş", value: "\(profile.age)")
                        ProfileInfoRow(icon: "figure.stand", title: "Boy", value: String(format: "%.0f cm", profile.height))
                        ProfileInfoRow(icon: "person.badge.shield.checkmark", title: "Cinsiyet", value: profile.gender)

                        Button(action: {
                            showingProfileEdit = true
                        }) {
                            HStack {
                                Image(systemName: "pencil")
                                Text("Profili Düzenle")
                            }
                        }
                    }
                }

                // Workout Plan Section
                Section("Antrenman Planı") {
                    if let plan = dataManager.currentWorkoutPlan {
                        ProfileInfoRow(icon: "list.bullet.clipboard", title: "Plan", value: plan.name)
                        ProfileInfoRow(icon: "figure.strengthtraining.traditional", title: "Vücut Tipi", value: plan.bodyType.rawValue)
                        ProfileInfoRow(icon: "target", title: "Hedef", value: plan.goal.rawValue)

                        Button(action: {
                            dataManager.generateWorkoutPlan()
                        }) {
                            HStack {
                                Image(systemName: "arrow.clockwise")
                                Text("Planı Yenile")
                            }
                        }
                    }
                }

                // Statistics Section
                Section("İstatistikler") {
                    ProfileInfoRow(
                        icon: "chart.bar.fill",
                        title: "Toplam Antrenman",
                        value: "\(dataManager.getTotalWorkouts())"
                    )

                    ProfileInfoRow(
                        icon: "calendar.badge.clock",
                        title: "Bu Hafta",
                        value: "\(dataManager.getWorkoutsThisWeek())"
                    )

                    if dataManager.getTotalWorkouts() > 0 {
                        ProfileInfoRow(
                            icon: "clock.fill",
                            title: "Ortalama Süre",
                            value: formatDuration(dataManager.getAverageWorkoutDuration())
                        )
                    }

                    ProfileInfoRow(
                        icon: "list.number",
                        title: "Kilo Kayıtları",
                        value: "\(dataManager.weightRecords.count)"
                    )
                }

                // App Info Section
                Section("Uygulama") {
                    HStack {
                        Image(systemName: "info.circle")
                        Text("Versiyon")
                        Spacer()
                        Text("1.0.0")
                            .foregroundColor(.secondary)
                    }

                    Link(destination: URL(string: "https://www.apple.com/health/")!) {
                        HStack {
                            Image(systemName: "heart.text.square")
                            Text("Sağlık & Fitness")
                            Spacer()
                            Image(systemName: "arrow.up.right")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                }

                // Data Management Section
                Section("Veri Yönetimi") {
                    Button(role: .destructive, action: {
                        showingResetAlert = true
                    }) {
                        HStack {
                            Image(systemName: "trash")
                            Text("Tüm Verileri Sil")
                        }
                    }
                }
            }
            .navigationTitle("Ayarlar")
            .alert("Tüm Verileri Sil", isPresented: $showingResetAlert) {
                Button("İptal", role: .cancel) { }
                Button("Sil", role: .destructive) {
                    dataManager.clearAllData()
                }
            } message: {
                Text("Bu işlem tüm profil, antrenman ve ilerleme verilerinizi silecektir. Bu işlem geri alınamaz.")
            }
            .sheet(isPresented: $showingProfileEdit) {
                EditProfileView()
            }
        }
    }

    func formatDuration(_ duration: TimeInterval) -> String {
        let minutes = Int(duration) / 60
        return "\(minutes) dk"
    }
}

struct ProfileInfoRow: View {
    let icon: String
    let title: String
    let value: String

    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(.blue)
                .frame(width: 30)

            Text(title)

            Spacer()

            Text(value)
                .foregroundColor(.secondary)
        }
    }
}

struct EditProfileView: View {
    @EnvironmentObject var dataManager: DataManager
    @Environment(\.dismiss) var dismiss

    @State private var name: String = ""
    @State private var age: String = ""
    @State private var height: String = ""
    @State private var targetWeight: String = ""
    @State private var selectedBodyType: BodyType = .mesomorph
    @State private var selectedGoal: FitnessGoal = .gainMuscle

    var body: some View {
        NavigationView {
            Form {
                Section("Kişisel Bilgiler") {
                    TextField("İsim", text: $name)
                    TextField("Yaş", text: $age)
                        .keyboardType(.numberPad)
                    TextField("Boy (cm)", text: $height)
                        .keyboardType(.decimalPad)
                }

                Section("Hedefler") {
                    Picker("Vücut Tipi", selection: $selectedBodyType) {
                        ForEach(BodyType.allCases, id: \.self) { type in
                            Text(type.rawValue).tag(type)
                        }
                    }

                    Picker("Hedef", selection: $selectedGoal) {
                        ForEach(FitnessGoal.allCases, id: \.self) { goal in
                            Text(goal.rawValue).tag(goal)
                        }
                    }

                    TextField("Hedef Kilo (kg)", text: $targetWeight)
                        .keyboardType(.decimalPad)
                }
            }
            .navigationTitle("Profili Düzenle")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("İptal") {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Kaydet") {
                        saveProfile()
                    }
                }
            }
            .onAppear {
                loadProfile()
            }
        }
    }

    func loadProfile() {
        guard let profile = dataManager.userProfile else { return }
        name = profile.name
        age = "\(profile.age)"
        height = "\(profile.height)"
        targetWeight = "\(profile.targetWeight)"
        selectedBodyType = profile.bodyType
        selectedGoal = profile.goal
    }

    func saveProfile() {
        guard let profile = dataManager.userProfile,
              let ageInt = Int(age),
              let heightDouble = Double(height),
              let targetWeightDouble = Double(targetWeight) else {
            return
        }

        let updatedProfile = UserProfile(
            id: profile.id,
            name: name,
            bodyType: selectedBodyType,
            currentWeight: profile.currentWeight,
            targetWeight: targetWeightDouble,
            goal: selectedGoal,
            height: heightDouble,
            age: ageInt,
            gender: profile.gender
        )

        dataManager.saveProfile(updatedProfile)
        dismiss()
    }
}

#Preview {
    SettingsView()
        .environmentObject(DataManager())
}
