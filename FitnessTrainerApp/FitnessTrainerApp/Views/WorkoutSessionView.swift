import SwiftUI

struct WorkoutSessionView: View {
    let workoutDay: WorkoutDay
    @EnvironmentObject var dataManager: DataManager
    @Environment(\.dismiss) var dismiss

    @State private var currentExerciseIndex = 0
    @State private var completedSets: [UUID: [CompletedSet]] = [:]
    @State private var startTime = Date()
    @State private var showingCompletion = false
    @State private var notes = ""

    var body: some View {
        VStack(spacing: 0) {
            // Progress Header
            progressHeader

            // Current Exercise
            if currentExerciseIndex < workoutDay.exercises.count {
                ScrollView {
                    VStack(spacing: 20) {
                        currentExerciseCard
                        setsTracker
                        exerciseInstructions
                    }
                    .padding()
                }
            }

            // Navigation Buttons
            navigationButtons
        }
        .navigationTitle(workoutDay.day.rawValue)
        .navigationBarTitleDisplayMode(.inline)
        .sheet(isPresented: $showingCompletion) {
            WorkoutCompletionView(
                workoutDay: workoutDay,
                completedExercises: buildCompletedExercises(),
                duration: Date().timeIntervalSince(startTime),
                onSave: saveWorkout
            )
        }
    }

    var progressHeader: some View {
        VStack(spacing: 8) {
            // Progress Bar
            ProgressView(value: Double(currentExerciseIndex), total: Double(workoutDay.exercises.count))
                .tint(.blue)

            // Progress Text
            HStack {
                Text("Egzersiz \(currentExerciseIndex + 1) / \(workoutDay.exercises.count)")
                    .font(.caption)
                    .foregroundColor(.secondary)

                Spacer()

                Text(formatElapsedTime())
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color.gray.opacity(0.05))
    }

    var currentExerciseCard: some View {
        let workoutExercise = workoutDay.exercises[currentExerciseIndex]

        return VStack(spacing: 15) {
            // Exercise Visual
            ZStack {
                LinearGradient(
                    colors: [.blue.opacity(0.3), .purple.opacity(0.3)],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )

                Image(systemName: workoutExercise.exercise.imageURL)
                    .font(.system(size: 80))
                    .foregroundColor(.white)
            }
            .frame(height: 200)
            .cornerRadius(15)

            // Exercise Info
            VStack(spacing: 10) {
                Text(workoutExercise.exercise.name)
                    .font(.title2)
                    .fontWeight(.bold)

                HStack(spacing: 15) {
                    InfoPill(icon: "repeat", text: "\(workoutExercise.sets) Set")
                    InfoPill(icon: "number", text: "\(workoutExercise.reps) Tekrar")
                    InfoPill(icon: "timer", text: "\(workoutExercise.restSeconds)sn")
                }

                if let notes = workoutExercise.notes {
                    Text(notes)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.orange.opacity(0.1))
                        .cornerRadius(8)
                }
            }
        }
    }

    var setsTracker: some View {
        let workoutExercise = workoutDay.exercises[currentExerciseIndex]
        let exerciseId = workoutExercise.exercise.id
        let completed = completedSets[exerciseId] ?? []

        return VStack(alignment: .leading, spacing: 15) {
            Text("Setler")
                .font(.headline)

            ForEach(0..<workoutExercise.sets, id: \.self) { setIndex in
                SetRow(
                    setNumber: setIndex + 1,
                    targetReps: workoutExercise.reps,
                    isCompleted: setIndex < completed.count,
                    completedSet: setIndex < completed.count ? completed[setIndex] : nil,
                    onComplete: { reps, weight in
                        addCompletedSet(exerciseId: exerciseId, reps: reps, weight: weight)
                    }
                )
            }
        }
        .padding()
        .background(Color.gray.opacity(0.05))
        .cornerRadius(12)
    }

    var exerciseInstructions: some View {
        let exercise = workoutDay.exercises[currentExerciseIndex].exercise

        return VStack(alignment: .leading, spacing: 12) {
            Text("Nasıl Yapılır?")
                .font(.headline)

            ForEach(Array(exercise.instructions.enumerated()), id: \.offset) { index, instruction in
                HStack(alignment: .top, spacing: 10) {
                    Text("\(index + 1)")
                        .font(.caption)
                        .fontWeight(.bold)
                        .foregroundColor(.white)
                        .frame(width: 20, height: 20)
                        .background(Circle().fill(Color.blue))

                    Text(instruction)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding()
        .background(Color.blue.opacity(0.05))
        .cornerRadius(12)
    }

    var navigationButtons: some View {
        HStack(spacing: 15) {
            if currentExerciseIndex > 0 {
                Button(action: previousExercise) {
                    Label("Önceki", systemImage: "chevron.left")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.bordered)
            }

            if currentExerciseIndex < workoutDay.exercises.count - 1 {
                Button(action: nextExercise) {
                    Label("Sonraki", systemImage: "chevron.right")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
            } else {
                Button(action: completeWorkout) {
                    Label("Bitir", systemImage: "checkmark")
                        .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .tint(.green)
            }
        }
        .padding()
        .background(Color.white)
        .shadow(color: .black.opacity(0.1), radius: 5, y: -2)
    }

    func addCompletedSet(exerciseId: UUID, reps: Int, weight: Double) {
        let set = CompletedSet(reps: reps, weight: weight)
        if completedSets[exerciseId] == nil {
            completedSets[exerciseId] = []
        }
        completedSets[exerciseId]?.append(set)
    }

    func previousExercise() {
        if currentExerciseIndex > 0 {
            withAnimation {
                currentExerciseIndex -= 1
            }
        }
    }

    func nextExercise() {
        if currentExerciseIndex < workoutDay.exercises.count - 1 {
            withAnimation {
                currentExerciseIndex += 1
            }
        }
    }

    func completeWorkout() {
        showingCompletion = true
    }

    func buildCompletedExercises() -> [CompletedExercise] {
        return workoutDay.exercises.compactMap { workoutExercise in
            guard let sets = completedSets[workoutExercise.exercise.id], !sets.isEmpty else {
                return nil
            }
            return CompletedExercise(
                exerciseId: workoutExercise.exercise.id,
                exerciseName: workoutExercise.exercise.name,
                completedSets: sets
            )
        }
    }

    func saveWorkout(notes: String) {
        let session = WorkoutSession(
            workoutDayId: workoutDay.id,
            completedExercises: buildCompletedExercises(),
            duration: Date().timeIntervalSince(startTime),
            notes: notes.isEmpty ? nil : notes
        )
        dataManager.saveWorkoutSession(session)
        dismiss()
    }

    func formatElapsedTime() -> String {
        let elapsed = Int(Date().timeIntervalSince(startTime))
        let minutes = elapsed / 60
        let seconds = elapsed % 60
        return String(format: "%02d:%02d", minutes, seconds)
    }
}

struct SetRow: View {
    let setNumber: Int
    let targetReps: Int
    let isCompleted: Bool
    let completedSet: CompletedSet?
    let onComplete: (Int, Double) -> Void

    @State private var showingInput = false
    @State private var reps = ""
    @State private var weight = ""

    var body: some View {
        HStack {
            Text("Set \(setNumber)")
                .font(.subheadline)
                .fontWeight(.semibold)
                .frame(width: 60, alignment: .leading)

            if isCompleted, let set = completedSet {
                HStack {
                    Text("\(set.reps) tekrar")
                        .font(.caption)
                    Text("•")
                    Text(String(format: "%.1f kg", set.weight))
                        .font(.caption)
                }
                .foregroundColor(.secondary)

                Spacer()

                Image(systemName: "checkmark.circle.fill")
                    .foregroundColor(.green)
            } else {
                Text("\(targetReps) tekrar hedef")
                    .font(.caption)
                    .foregroundColor(.secondary)

                Spacer()

                Button("Tamamla") {
                    showingInput = true
                }
                .buttonStyle(.bordered)
                .controlSize(.small)
            }
        }
        .padding()
        .background(isCompleted ? Color.green.opacity(0.1) : Color.gray.opacity(0.05))
        .cornerRadius(8)
        .sheet(isPresented: $showingInput) {
            SetInputView(
                setNumber: setNumber,
                targetReps: targetReps,
                onSave: { r, w in
                    onComplete(r, w)
                    showingInput = false
                }
            )
        }
    }
}

struct SetInputView: View {
    let setNumber: Int
    let targetReps: Int
    let onSave: (Int, Double) -> Void

    @Environment(\.dismiss) var dismiss
    @State private var reps: String
    @State private var weight: String = ""

    init(setNumber: Int, targetReps: Int, onSave: @escaping (Int, Double) -> Void) {
        self.setNumber = setNumber
        self.targetReps = targetReps
        self.onSave = onSave
        _reps = State(initialValue: "\(targetReps)")
    }

    var body: some View {
        NavigationView {
            Form {
                Section("Set \(setNumber)") {
                    HStack {
                        Text("Tekrar")
                        TextField("Tekrar sayısı", text: $reps)
                            .keyboardType(.numberPad)
                            .multilineTextAlignment(.trailing)
                    }

                    HStack {
                        Text("Ağırlık (kg)")
                        TextField("0", text: $weight)
                            .keyboardType(.decimalPad)
                            .multilineTextAlignment(.trailing)
                    }
                }
            }
            .navigationTitle("Set Bilgisi")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("İptal") {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Kaydet") {
                        if let r = Int(reps), let w = Double(weight.isEmpty ? "0" : weight) {
                            onSave(r, w)
                        }
                    }
                }
            }
        }
        .presentationDetents([.medium])
    }
}

struct InfoPill: View {
    let icon: String
    let text: String

    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: icon)
                .font(.caption)
            Text(text)
                .font(.caption)
        }
        .padding(.horizontal, 10)
        .padding(.vertical, 6)
        .background(Color.blue.opacity(0.1))
        .cornerRadius(8)
    }
}

struct WorkoutCompletionView: View {
    let workoutDay: WorkoutDay
    let completedExercises: [CompletedExercise]
    let duration: TimeInterval
    let onSave: (String) -> Void

    @Environment(\.dismiss) var dismiss
    @State private var notes = ""

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 25) {
                    // Success Icon
                    Image(systemName: "checkmark.circle.fill")
                        .font(.system(size: 80))
                        .foregroundColor(.green)

                    Text("Tebrikler! 🎉")
                        .font(.title)
                        .fontWeight(.bold)

                    Text("Antrenmanını Tamamladın")
                        .font(.headline)
                        .foregroundColor(.secondary)

                    // Stats
                    VStack(spacing: 15) {
                        StatRow(title: "Süre", value: formatDuration(duration))
                        StatRow(title: "Egzersiz", value: "\(completedExercises.count)")
                        StatRow(title: "Toplam Set", value: "\(totalSets)")
                    }
                    .padding()
                    .background(Color.gray.opacity(0.05))
                    .cornerRadius(12)

                    // Notes
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Notlar (İsteğe Bağlı)")
                            .font(.headline)

                        TextEditor(text: $notes)
                            .frame(height: 100)
                            .padding(8)
                            .background(Color.gray.opacity(0.05))
                            .cornerRadius(8)
                    }

                    Button(action: {
                        onSave(notes)
                        dismiss()
                    }) {
                        Text("Kaydet ve Bitir")
                            .fontWeight(.semibold)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.green)
                            .foregroundColor(.white)
                            .cornerRadius(12)
                    }
                }
                .padding()
            }
            .navigationTitle("Antrenman Tamamlandı")
            .navigationBarTitleDisplayMode(.inline)
        }
    }

    var totalSets: Int {
        completedExercises.reduce(0) { $0 + $1.completedSets.count }
    }

    func formatDuration(_ duration: TimeInterval) -> String {
        let minutes = Int(duration) / 60
        return "\(minutes) dakika"
    }
}

struct StatRow: View {
    let title: String
    let value: String

    var body: some View {
        HStack {
            Text(title)
                .foregroundColor(.secondary)
            Spacer()
            Text(value)
                .fontWeight(.semibold)
        }
    }
}

#Preview {
    NavigationView {
        WorkoutSessionView(
            workoutDay: WorkoutDay(
                day: .monday,
                muscleGroups: [.chest],
                exercises: []
            )
        )
        .environmentObject(DataManager())
    }
}
