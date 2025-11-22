import SwiftUI

struct WorkoutPlanView: View {
    @EnvironmentObject var dataManager: DataManager

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    if let plan = dataManager.currentWorkoutPlan {
                        // Plan Info Card
                        planInfoCard(plan: plan)

                        // Workout Days
                        ForEach(plan.workoutDays) { workoutDay in
                            WorkoutDayCard(workoutDay: workoutDay)
                        }
                    } else {
                        emptyStateView
                    }
                }
                .padding()
            }
            .navigationTitle("Antrenman Programım")
        }
    }

    func planInfoCard(plan: WorkoutPlan) -> some View {
        VStack(alignment: .leading, spacing: 12) {
            Text(plan.name)
                .font(.title2)
                .fontWeight(.bold)

            HStack {
                Label(plan.bodyType.rawValue, systemImage: "person.fill")
                    .font(.caption)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(Color.blue.opacity(0.2))
                    .cornerRadius(8)

                Label(plan.goal.rawValue, systemImage: "target")
                    .font(.caption)
                    .padding(.horizontal, 10)
                    .padding(.vertical, 6)
                    .background(Color.green.opacity(0.2))
                    .cornerRadius(8)
            }

            Divider()

            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Haftalık Gün")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text("\(plan.workoutDays.count)")
                        .font(.title3)
                        .fontWeight(.semibold)
                }

                Spacer()

                VStack(alignment: .leading, spacing: 4) {
                    Text("Toplam Egzersiz")
                        .font(.caption)
                        .foregroundColor(.secondary)
                    Text("\(totalExercises(in: plan))")
                        .font(.title3)
                        .fontWeight(.semibold)
                }

                Spacer()
            }
        }
        .padding()
        .background(
            LinearGradient(colors: [.purple.opacity(0.1), .blue.opacity(0.1)], startPoint: .topLeading, endPoint: .bottomTrailing)
        )
        .cornerRadius(15)
    }

    var emptyStateView: some View {
        VStack(spacing: 20) {
            Image(systemName: "doc.text.magnifyingglass")
                .font(.system(size: 60))
                .foregroundColor(.secondary)

            Text("Antrenman Programı Bulunamadı")
                .font(.headline)

            Text("Profilinizi güncelleyerek yeni bir program oluşturabilirsiniz")
                .font(.caption)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .padding()
    }

    func totalExercises(in plan: WorkoutPlan) -> Int {
        plan.workoutDays.reduce(0) { $0 + $1.exercises.count }
    }
}

struct WorkoutDayCard: View {
    let workoutDay: WorkoutDay
    @State private var isExpanded = false

    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Header
            Button(action: {
                withAnimation {
                    isExpanded.toggle()
                }
            }) {
                HStack {
                    VStack(alignment: .leading, spacing: 8) {
                        Text(workoutDay.day.rawValue)
                            .font(.headline)
                            .foregroundColor(.primary)

                        HStack {
                            ForEach(workoutDay.muscleGroups, id: \.self) { muscle in
                                Text(muscle.rawValue)
                                    .font(.caption)
                                    .padding(.horizontal, 8)
                                    .padding(.vertical, 4)
                                    .background(Color.blue.opacity(0.2))
                                    .cornerRadius(6)
                            }
                        }
                    }

                    Spacer()

                    VStack(alignment: .trailing, spacing: 4) {
                        Image(systemName: isExpanded ? "chevron.up" : "chevron.down")
                            .foregroundColor(.secondary)

                        Text("\(workoutDay.exercises.count) egzersiz")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                .padding()
                .background(Color.gray.opacity(0.05))
            }
            .buttonStyle(.plain)

            // Exercises List
            if isExpanded {
                VStack(spacing: 0) {
                    ForEach(Array(workoutDay.exercises.enumerated()), id: \.element.id) { index, workoutExercise in
                        NavigationLink(destination: ExerciseDetailView(exercise: workoutExercise.exercise)) {
                            ExerciseRowView(workoutExercise: workoutExercise, index: index + 1)
                        }
                        .buttonStyle(.plain)

                        if index < workoutDay.exercises.count - 1 {
                            Divider()
                                .padding(.leading, 60)
                        }
                    }
                }
                .background(Color.white)
            }
        }
        .cornerRadius(12)
        .shadow(color: .black.opacity(0.05), radius: 5, x: 0, y: 2)
    }
}

struct ExerciseRowView: View {
    let workoutExercise: WorkoutExercise
    let index: Int

    var body: some View {
        HStack(spacing: 15) {
            // Exercise Number
            Text("\(index)")
                .font(.headline)
                .foregroundColor(.white)
                .frame(width: 30, height: 30)
                .background(Circle().fill(Color.blue))

            // Exercise Info
            VStack(alignment: .leading, spacing: 6) {
                Text(workoutExercise.exercise.name)
                    .font(.subheadline)
                    .fontWeight(.semibold)

                HStack(spacing: 12) {
                    Label("\(workoutExercise.sets) set", systemImage: "repeat")
                        .font(.caption)
                        .foregroundColor(.secondary)

                    Label("\(workoutExercise.reps) tekrar", systemImage: "number")
                        .font(.caption)
                        .foregroundColor(.secondary)

                    if workoutExercise.restSeconds > 0 {
                        Label("\(workoutExercise.restSeconds)sn", systemImage: "timer")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }

            Spacer()

            Image(systemName: "chevron.right")
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
    }
}

#Preview {
    WorkoutPlanView()
        .environmentObject(DataManager())
}
