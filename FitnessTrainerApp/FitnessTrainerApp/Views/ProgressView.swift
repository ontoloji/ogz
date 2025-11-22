import SwiftUI
import Charts

struct ProgressView: View {
    @EnvironmentObject var dataManager: DataManager
    @State private var showingAddWeight = false

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 25) {
                    // Weight Progress Card
                    weightProgressCard

                    // Weight Chart
                    weightChartCard

                    // Goals Card
                    goalsCard

                    // Weight History
                    weightHistorySection

                    // Add Weight Button
                    Button(action: {
                        showingAddWeight = true
                    }) {
                        Label("Yeni Kilo Kaydı Ekle", systemImage: "plus.circle.fill")
                            .font(.headline)
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(12)
                    }
                }
                .padding()
            }
            .navigationTitle("İlerleme")
            .sheet(isPresented: $showingAddWeight) {
                AddWeightView()
            }
        }
    }

    var weightProgressCard: some View {
        VStack(spacing: 15) {
            if let progress = dataManager.getWeightProgress() {
                HStack {
                    VStack(alignment: .leading, spacing: 8) {
                        Text("Mevcut Kilo")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text(String(format: "%.1f kg", progress.current))
                            .font(.title)
                            .fontWeight(.bold)
                    }

                    Spacer()

                    VStack(alignment: .trailing, spacing: 8) {
                        Text("Hedef")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text(String(format: "%.1f kg", progress.target))
                            .font(.title2)
                            .fontWeight(.semibold)
                            .foregroundColor(.blue)
                    }
                }

                Divider()

                // Progress Bar
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Text("Hedefe")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Spacer()
                        Text(String(format: "%.1f kg kaldı", abs(progress.current - progress.target)))
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    GeometryReader { geometry in
                        ZStack(alignment: .leading) {
                            Rectangle()
                                .fill(Color.gray.opacity(0.2))
                                .frame(height: 8)
                                .cornerRadius(4)

                            Rectangle()
                                .fill(Color.blue)
                                .frame(width: calculateProgress(current: progress.current, target: progress.target, width: geometry.size.width), height: 8)
                                .cornerRadius(4)
                        }
                    }
                    .frame(height: 8)
                }

                if abs(progress.change) > 0 {
                    HStack {
                        Image(systemName: progress.change > 0 ? "arrow.up.right" : "arrow.down.right")
                            .foregroundColor(progress.change > 0 ? .red : .green)
                        Text(String(format: "%.1f kg %@", abs(progress.change), progress.change > 0 ? "arttı" : "azaldı"))
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
            }
        }
        .padding()
        .background(
            LinearGradient(colors: [.blue.opacity(0.1), .purple.opacity(0.1)], startPoint: .topLeading, endPoint: .bottomTrailing)
        )
        .cornerRadius(15)
    }

    var weightChartCard: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Kilo Grafiği")
                .font(.headline)

            if dataManager.weightRecords.count >= 2 {
                Chart {
                    ForEach(dataManager.weightRecords.reversed()) { record in
                        LineMark(
                            x: .value("Tarih", record.date),
                            y: .value("Kilo", record.weight)
                        )
                        .foregroundStyle(Color.blue)

                        PointMark(
                            x: .value("Tarih", record.date),
                            y: .value("Kilo", record.weight)
                        )
                        .foregroundStyle(Color.blue)
                    }

                    if let targetWeight = dataManager.userProfile?.targetWeight {
                        RuleMark(y: .value("Hedef", targetWeight))
                            .foregroundStyle(Color.green.opacity(0.5))
                            .lineStyle(StrokeStyle(lineWidth: 2, dash: [5, 5]))
                            .annotation(position: .top, alignment: .trailing) {
                                Text("Hedef")
                                    .font(.caption2)
                                    .foregroundColor(.green)
                            }
                    }
                }
                .frame(height: 200)
                .chartXAxis {
                    AxisMarks(values: .automatic) { _ in
                        AxisValueLabel(format: .dateTime.month().day())
                    }
                }
            } else {
                VStack(spacing: 10) {
                    Image(systemName: "chart.line.uptrend.xyaxis")
                        .font(.largeTitle)
                        .foregroundColor(.secondary)
                    Text("Grafik için en az 2 kilo kaydı gerekli")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity)
                .frame(height: 200)
                .background(Color.gray.opacity(0.05))
                .cornerRadius(12)
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(15)
        .shadow(color: .black.opacity(0.05), radius: 5)
    }

    var goalsCard: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Hedeflerim")
                .font(.headline)

            if let profile = dataManager.userProfile {
                VStack(spacing: 12) {
                    GoalRow(
                        icon: "target",
                        title: "Ana Hedef",
                        value: profile.goal.rawValue,
                        color: .blue
                    )

                    GoalRow(
                        icon: "figure.strengthtraining.traditional",
                        title: "Vücut Tipi",
                        value: profile.bodyType.rawValue,
                        color: .green
                    )

                    if let bmi = calculateBMI(weight: profile.currentWeight, height: profile.height) {
                        GoalRow(
                            icon: "heart.text.square",
                            title: "BMI",
                            value: String(format: "%.1f", bmi),
                            color: .orange
                        )
                    }
                }
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(15)
        .shadow(color: .black.opacity(0.05), radius: 5)
    }

    var weightHistorySection: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Kilo Geçmişi")
                .font(.headline)

            if dataManager.weightRecords.isEmpty {
                VStack(spacing: 10) {
                    Image(systemName: "list.bullet.clipboard")
                        .font(.largeTitle)
                        .foregroundColor(.secondary)
                    Text("Henüz kilo kaydın yok")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.gray.opacity(0.05))
                .cornerRadius(12)
            } else {
                ForEach(dataManager.weightRecords) { record in
                    WeightRecordRow(record: record)
                }
            }
        }
    }

    func calculateProgress(current: Double, target: Double, width: CGFloat) -> CGFloat {
        // Başlangıç kilosunu al
        let start = dataManager.weightRecords.last?.weight ?? current

        if start == target {
            return width
        }

        let totalDistance = abs(target - start)
        let currentDistance = abs(current - start)
        let progress = min(currentDistance / totalDistance, 1.0)

        return width * CGFloat(progress)
    }

    func calculateBMI(weight: Double, height: Double) -> Double? {
        guard height > 0 else { return nil }
        let heightInMeters = height / 100.0
        return weight / (heightInMeters * heightInMeters)
    }
}

struct GoalRow: View {
    let icon: String
    let title: String
    let value: String
    let color: Color

    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(color)
                .frame(width: 30)

            VStack(alignment: .leading, spacing: 2) {
                Text(title)
                    .font(.caption)
                    .foregroundColor(.secondary)
                Text(value)
                    .font(.subheadline)
                    .fontWeight(.semibold)
            }

            Spacer()
        }
        .padding()
        .background(color.opacity(0.1))
        .cornerRadius(10)
    }
}

struct WeightRecordRow: View {
    let record: WeightRecord
    @EnvironmentObject var dataManager: DataManager

    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(String(format: "%.1f kg", record.weight))
                    .font(.headline)

                Text(formatDate(record.date))
                    .font(.caption)
                    .foregroundColor(.secondary)

                if let notes = record.notes {
                    Text(notes)
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .italic()
                }
            }

            Spacer()

            Button(action: {
                dataManager.deleteWeightRecord(record)
            }) {
                Image(systemName: "trash")
                    .foregroundColor(.red)
            }
        }
        .padding()
        .background(Color.gray.opacity(0.05))
        .cornerRadius(10)
    }

    func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.locale = Locale(identifier: "tr_TR")
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

struct AddWeightView: View {
    @EnvironmentObject var dataManager: DataManager
    @Environment(\.dismiss) var dismiss

    @State private var weight = ""
    @State private var notes = ""

    var body: some View {
        NavigationView {
            Form {
                Section("Kilo Bilgisi") {
                    HStack {
                        Text("Kilo (kg)")
                        TextField("Örn: 70.5", text: $weight)
                            .keyboardType(.decimalPad)
                            .multilineTextAlignment(.trailing)
                    }
                }

                Section("Notlar (İsteğe Bağlı)") {
                    TextEditor(text: $notes)
                        .frame(height: 100)
                }
            }
            .navigationTitle("Yeni Kilo Kaydı")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("İptal") {
                        dismiss()
                    }
                }
                ToolbarItem(placement: .confirmationAction) {
                    Button("Kaydet") {
                        saveWeight()
                    }
                    .disabled(weight.isEmpty)
                }
            }
        }
    }

    func saveWeight() {
        guard let weightValue = Double(weight) else { return }

        let record = WeightRecord(
            weight: weightValue,
            notes: notes.isEmpty ? nil : notes
        )

        dataManager.addWeightRecord(record)
        dismiss()
    }
}

#Preview {
    ProgressView()
        .environmentObject(DataManager())
}
