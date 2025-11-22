import SwiftUI

struct HomeView: View {
    @EnvironmentObject var dataManager: DataManager

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Greeting Card
                    greetingCard

                    // Quick Stats
                    quickStatsSection

                    // Today's Workout
                    todaysWorkoutSection

                    // Recent Activity
                    recentActivitySection
                }
                .padding()
            }
            .navigationTitle("Ana Sayfa")
        }
    }

    var greetingCard: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Merhaba, \(dataManager.userProfile?.name ?? "Sporcu")! 💪")
                .font(.title2)
                .fontWeight(.bold)

            Text("Bugün \(formattedDate)")
                .font(.subheadline)
                .foregroundColor(.secondary)

            if let profile = dataManager.userProfile {
                HStack(spacing: 15) {
                    StatBadge(title: "Hedef", value: profile.goal.rawValue, color: .blue)
                    StatBadge(title: "Vücut Tipi", value: profile.bodyType.rawValue, color: .green)
                }
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding()
        .background(
            LinearGradient(colors: [.blue.opacity(0.1), .purple.opacity(0.1)], startPoint: .topLeading, endPoint: .bottomTrailing)
        )
        .cornerRadius(15)
    }

    var quickStatsSection: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("İstatistikler")
                .font(.headline)

            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 15) {
                StatCard(
                    title: "Toplam Antrenman",
                    value: "\(dataManager.getTotalWorkouts())",
                    icon: "figure.strengthtraining.traditional",
                    color: .blue
                )

                StatCard(
                    title: "Bu Hafta",
                    value: "\(dataManager.getWorkoutsThisWeek())",
                    icon: "calendar",
                    color: .green
                )

                if let progress = dataManager.getWeightProgress() {
                    StatCard(
                        title: "Mevcut Kilo",
                        value: String(format: "%.1f kg", progress.current),
                        icon: "scalemass",
                        color: .orange
                    )

                    StatCard(
                        title: "Hedef",
                        value: String(format: "%.1f kg", progress.target),
                        icon: "flag.fill",
                        color: .purple
                    )
                }
            }
        }
    }

    var todaysWorkoutSection: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Bugünün Antrenmanı")
                .font(.headline)

            if let todayWorkout = getTodayWorkout() {
                NavigationLink(destination: WorkoutSessionView(workoutDay: todayWorkout)) {
                    HStack {
                        VStack(alignment: .leading, spacing: 8) {
                            Text(todayWorkout.day.rawValue)
                                .font(.title3)
                                .fontWeight(.semibold)

                            HStack {
                                ForEach(todayWorkout.muscleGroups, id: \.self) { muscle in
                                    Text(muscle.rawValue)
                                        .font(.caption)
                                        .padding(.horizontal, 8)
                                        .padding(.vertical, 4)
                                        .background(Color.blue.opacity(0.2))
                                        .cornerRadius(8)
                                }
                            }

                            Text("\(todayWorkout.exercises.count) egzersiz")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }

                        Spacer()

                        Image(systemName: "chevron.right")
                            .foregroundColor(.secondary)
                    }
                    .padding()
                    .background(Color.blue.opacity(0.1))
                    .cornerRadius(12)
                }
                .buttonStyle(.plain)
            } else {
                VStack(spacing: 10) {
                    Image(systemName: "bed.double.fill")
                        .font(.largeTitle)
                        .foregroundColor(.secondary)
                    Text("Bugün dinlenme günün!")
                        .font(.headline)
                    Text("Vücudunun iyileşmesine izin ver")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(12)
            }
        }
    }

    var recentActivitySection: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Son Aktiviteler")
                .font(.headline)

            if dataManager.workoutSessions.isEmpty {
                VStack(spacing: 10) {
                    Image(systemName: "figure.walk")
                        .font(.largeTitle)
                        .foregroundColor(.secondary)
                    Text("Henüz antrenman kaydın yok")
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.gray.opacity(0.1))
                .cornerRadius(12)
            } else {
                ForEach(dataManager.workoutSessions.prefix(3)) { session in
                    ActivityRow(session: session)
                }
            }
        }
    }

    var formattedDate: String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "tr_TR")
        formatter.dateFormat = "d MMMM yyyy, EEEE"
        return formatter.string(from: Date())
    }

    func getTodayWorkout() -> WorkoutDay? {
        guard let plan = dataManager.currentWorkoutPlan else { return nil }

        let calendar = Calendar.current
        let weekday = calendar.component(.weekday, from: Date())

        // Convert to our WeekDay enum (Sunday = 1 in Calendar, but we want Monday = 0)
        let dayIndex = (weekday + 5) % 7
        let weekDays: [WeekDay] = [.monday, .tuesday, .wednesday, .thursday, .friday, .saturday, .sunday]

        let today = weekDays[dayIndex]
        return plan.workoutDays.first { $0.day == today }
    }
}

struct StatBadge: View {
    let title: String
    let value: String
    let color: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
            Text(value)
                .font(.subheadline)
                .fontWeight(.semibold)
                .foregroundColor(color)
        }
        .padding(.horizontal, 12)
        .padding(.vertical, 8)
        .background(color.opacity(0.1))
        .cornerRadius(8)
    }
}

struct StatCard: View {
    let title: String
    let value: String
    let icon: String
    let color: Color

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(color)
                Spacer()
            }

            Text(value)
                .font(.title2)
                .fontWeight(.bold)

            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .background(color.opacity(0.1))
        .cornerRadius(12)
    }
}

struct ActivityRow: View {
    let session: WorkoutSession

    var body: some View {
        HStack {
            Image(systemName: "checkmark.circle.fill")
                .foregroundColor(.green)
                .font(.title2)

            VStack(alignment: .leading, spacing: 4) {
                Text("Antrenman Tamamlandı")
                    .font(.subheadline)
                    .fontWeight(.semibold)

                Text("\(session.completedExercises.count) egzersiz • \(formatDuration(session.duration))")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            Spacer()

            Text(formatDate(session.date))
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .background(Color.gray.opacity(0.05))
        .cornerRadius(10)
    }

    func formatDuration(_ duration: TimeInterval) -> String {
        let minutes = Int(duration) / 60
        return "\(minutes) dk"
    }

    func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "tr_TR")
        formatter.dateFormat = "d MMM"
        return formatter.string(from: date)
    }
}

#Preview {
    HomeView()
        .environmentObject(DataManager())
}
