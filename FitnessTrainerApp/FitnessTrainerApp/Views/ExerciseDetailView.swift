import SwiftUI

struct ExerciseDetailView: View {
    let exercise: Exercise

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 25) {
                // Exercise Image/Icon
                exerciseVisual

                // Exercise Info
                VStack(alignment: .leading, spacing: 15) {
                    // Title
                    Text(exercise.name)
                        .font(.title)
                        .fontWeight(.bold)

                    // Badges
                    HStack {
                        Badge(text: exercise.muscleGroup.rawValue, color: .blue)
                        Badge(text: exercise.difficulty.rawValue, color: difficultyColor)
                    }

                    Divider()

                    // Description
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Açıklama")
                            .font(.headline)
                        Text(exercise.description)
                            .font(.body)
                            .foregroundColor(.secondary)
                    }

                    Divider()

                    // Instructions
                    VStack(alignment: .leading, spacing: 12) {
                        Text("Nasıl Yapılır?")
                            .font(.headline)

                        ForEach(Array(exercise.instructions.enumerated()), id: \.offset) { index, instruction in
                            HStack(alignment: .top, spacing: 12) {
                                Text("\(index + 1)")
                                    .font(.caption)
                                    .fontWeight(.bold)
                                    .foregroundColor(.white)
                                    .frame(width: 24, height: 24)
                                    .background(Circle().fill(Color.blue))

                                Text(instruction)
                                    .font(.body)
                                    .fixedSize(horizontal: false, vertical: true)

                                Spacer()
                            }
                        }
                    }

                    Divider()

                    // Tips
                    VStack(alignment: .leading, spacing: 8) {
                        Label("İpuçları", systemImage: "lightbulb.fill")
                            .font(.headline)
                            .foregroundColor(.orange)

                        VStack(alignment: .leading, spacing: 8) {
                            TipRow(icon: "exclamationmark.triangle", text: "Harekete başlamadan önce ısınma yapın")
                            TipRow(icon: "figure.stand", text: "Form ve tekniğe odaklanın")
                            TipRow(icon: "arrow.up.arrow.down", text: "Kontrollü hareket edin")
                            TipRow(icon: "wind", text: "Düzenli nefes alın")
                        }
                    }
                    .padding()
                    .background(Color.orange.opacity(0.05))
                    .cornerRadius(12)
                }
                .padding()
            }
        }
        .navigationBarTitleDisplayMode(.inline)
    }

    var exerciseVisual: some View {
        ZStack {
            // Gradient Background
            LinearGradient(
                colors: [.blue.opacity(0.3), .purple.opacity(0.3)],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )

            // SF Symbol
            Image(systemName: exercise.imageURL)
                .font(.system(size: 100))
                .foregroundColor(.white)
        }
        .frame(height: 250)
        .frame(maxWidth: .infinity)
    }

    var difficultyColor: Color {
        switch exercise.difficulty {
        case .beginner:
            return .green
        case .intermediate:
            return .orange
        case .advanced:
            return .red
        }
    }
}

struct Badge: View {
    let text: String
    let color: Color

    var body: some View {
        Text(text)
            .font(.caption)
            .fontWeight(.medium)
            .padding(.horizontal, 12)
            .padding(.vertical, 6)
            .background(color.opacity(0.2))
            .foregroundColor(color)
            .cornerRadius(8)
    }
}

struct TipRow: View {
    let icon: String
    let text: String

    var body: some View {
        HStack(spacing: 10) {
            Image(systemName: icon)
                .foregroundColor(.orange)
                .frame(width: 20)

            Text(text)
                .font(.caption)
                .foregroundColor(.secondary)
        }
    }
}

#Preview {
    NavigationView {
        ExerciseDetailView(
            exercise: Exercise(
                name: "Barbell Bench Press",
                muscleGroup: .chest,
                difficulty: .intermediate,
                description: "Klasik göğüs geliştirme hareketi",
                instructions: [
                    "Düz benche sırt üstü uzanın",
                    "Barı omuz genişliğinden biraz daha geniş tutun",
                    "Barı göğsünüze doğru indirin",
                    "Kontrollü şekilde yukarı itin"
                ],
                imageURL: "figure.strengthtraining.traditional"
            )
        )
    }
}
