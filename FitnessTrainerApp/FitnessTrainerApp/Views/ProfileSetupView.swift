import SwiftUI

struct ProfileSetupView: View {
    @EnvironmentObject var dataManager: DataManager
    @State private var name = ""
    @State private var age = ""
    @State private var height = ""
    @State private var currentWeight = ""
    @State private var targetWeight = ""
    @State private var selectedBodyType: BodyType = .mesomorph
    @State private var selectedGoal: FitnessGoal = .gainMuscle
    @State private var selectedGender = "Erkek"
    @State private var currentStep = 0

    let genders = ["Erkek", "Kadın"]

    var body: some View {
        NavigationView {
            VStack(spacing: 20) {
                // Progress Indicator
                ProgressView(value: Double(currentStep), total: 3)
                    .padding()

                TabView(selection: $currentStep) {
                    // Step 1: Basic Info
                    basicInfoStep
                        .tag(0)

                    // Step 2: Body Type and Goal
                    bodyTypeGoalStep
                        .tag(1)

                    // Step 3: Measurements
                    measurementsStep
                        .tag(2)
                }
                .tabViewStyle(.page(indexDisplayMode: .never))

                // Navigation Buttons
                HStack {
                    if currentStep > 0 {
                        Button("Geri") {
                            withAnimation {
                                currentStep -= 1
                            }
                        }
                        .buttonStyle(.bordered)
                    }

                    Spacer()

                    if currentStep < 2 {
                        Button("İleri") {
                            withAnimation {
                                currentStep += 1
                            }
                        }
                        .buttonStyle(.borderedProminent)
                        .disabled(!canProceed)
                    } else {
                        Button("Başla") {
                            saveProfile()
                        }
                        .buttonStyle(.borderedProminent)
                        .disabled(!canComplete)
                    }
                }
                .padding()
            }
            .navigationTitle("Profil Oluştur")
        }
    }

    var basicInfoStep: some View {
        VStack(spacing: 20) {
            Text("Hadi Tanışalım!")
                .font(.largeTitle)
                .fontWeight(.bold)

            VStack(alignment: .leading, spacing: 15) {
                VStack(alignment: .leading) {
                    Text("Adın")
                        .font(.headline)
                    TextField("İsim", text: $name)
                        .textFieldStyle(.roundedBorder)
                }

                VStack(alignment: .leading) {
                    Text("Yaş")
                        .font(.headline)
                    TextField("Yaşınız", text: $age)
                        .keyboardType(.numberPad)
                        .textFieldStyle(.roundedBorder)
                }

                VStack(alignment: .leading) {
                    Text("Cinsiyet")
                        .font(.headline)
                    Picker("Cinsiyet", selection: $selectedGender) {
                        ForEach(genders, id: \.self) { gender in
                            Text(gender).tag(gender)
                        }
                    }
                    .pickerStyle(.segmented)
                }
            }
            .padding()

            Spacer()
        }
        .padding()
    }

    var bodyTypeGoalStep: some View {
        VStack(spacing: 20) {
            Text("Vücut Tipin ve Hedefin")
                .font(.largeTitle)
                .fontWeight(.bold)

            VStack(alignment: .leading, spacing: 20) {
                VStack(alignment: .leading) {
                    Text("Vücut Tipin")
                        .font(.headline)

                    ForEach(BodyType.allCases, id: \.self) { bodyType in
                        Button(action: {
                            selectedBodyType = bodyType
                        }) {
                            HStack {
                                VStack(alignment: .leading, spacing: 5) {
                                    Text(bodyType.rawValue)
                                        .font(.headline)
                                    Text(bodyType.description)
                                        .font(.caption)
                                        .foregroundColor(.secondary)
                                }
                                Spacer()
                                if selectedBodyType == bodyType {
                                    Image(systemName: "checkmark.circle.fill")
                                        .foregroundColor(.blue)
                                }
                            }
                            .padding()
                            .background(
                                RoundedRectangle(cornerRadius: 10)
                                    .fill(selectedBodyType == bodyType ? Color.blue.opacity(0.1) : Color.gray.opacity(0.1))
                            )
                        }
                        .buttonStyle(.plain)
                    }
                }

                VStack(alignment: .leading) {
                    Text("Hedefin")
                        .font(.headline)

                    ForEach(FitnessGoal.allCases, id: \.self) { goal in
                        Button(action: {
                            selectedGoal = goal
                        }) {
                            HStack {
                                Text(goal.rawValue)
                                    .font(.headline)
                                Spacer()
                                if selectedGoal == goal {
                                    Image(systemName: "checkmark.circle.fill")
                                        .foregroundColor(.blue)
                                }
                            }
                            .padding()
                            .background(
                                RoundedRectangle(cornerRadius: 10)
                                    .fill(selectedGoal == goal ? Color.blue.opacity(0.1) : Color.gray.opacity(0.1))
                            )
                        }
                        .buttonStyle(.plain)
                    }
                }
            }
            .padding()

            Spacer()
        }
        .padding()
    }

    var measurementsStep: some View {
        VStack(spacing: 20) {
            Text("Ölçülerin")
                .font(.largeTitle)
                .fontWeight(.bold)

            VStack(alignment: .leading, spacing: 15) {
                VStack(alignment: .leading) {
                    Text("Boy (cm)")
                        .font(.headline)
                    TextField("Örn: 175", text: $height)
                        .keyboardType(.decimalPad)
                        .textFieldStyle(.roundedBorder)
                }

                VStack(alignment: .leading) {
                    Text("Mevcut Kilo (kg)")
                        .font(.headline)
                    TextField("Örn: 70", text: $currentWeight)
                        .keyboardType(.decimalPad)
                        .textFieldStyle(.roundedBorder)
                }

                VStack(alignment: .leading) {
                    Text("Hedef Kilo (kg)")
                        .font(.headline)
                    TextField("Örn: 75", text: $targetWeight)
                        .keyboardType(.decimalPad)
                        .textFieldStyle(.roundedBorder)
                }
            }
            .padding()

            Spacer()
        }
        .padding()
    }

    var canProceed: Bool {
        switch currentStep {
        case 0:
            return !name.isEmpty && !age.isEmpty
        case 1:
            return true
        default:
            return false
        }
    }

    var canComplete: Bool {
        return !height.isEmpty && !currentWeight.isEmpty && !targetWeight.isEmpty
    }

    func saveProfile() {
        guard let ageInt = Int(age),
              let heightDouble = Double(height),
              let currentWeightDouble = Double(currentWeight),
              let targetWeightDouble = Double(targetWeight) else {
            return
        }

        let profile = UserProfile(
            name: name,
            bodyType: selectedBodyType,
            currentWeight: currentWeightDouble,
            targetWeight: targetWeightDouble,
            goal: selectedGoal,
            height: heightDouble,
            age: ageInt,
            gender: selectedGender
        )

        dataManager.saveProfile(profile)

        // İlk kilo kaydını ekle
        let initialWeightRecord = WeightRecord(weight: currentWeightDouble, notes: "Başlangıç kilosu")
        dataManager.addWeightRecord(initialWeightRecord)
    }
}

#Preview {
    ProfileSetupView()
        .environmentObject(DataManager())
}
