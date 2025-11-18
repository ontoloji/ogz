//
//  AnalyticsView.swift
//  PersonalAssistant
//
//  Productivity analytics and statistics view
//

import SwiftUI
import Charts

struct AnalyticsView: View {
    @Environment(\.managedObjectContext) private var viewContext

    @FetchRequest(
        fetchRequest: Task.fetchRequest(),
        animation: .default
    )
    private var allTasks: FetchedResults<Task>

    @FetchRequest(
        fetchRequest: FocusSession.fetchRequest(),
        animation: .default
    )
    private var focusSessions: FetchedResults<FocusSession>

    @State private var selectedPeriod: TimePeriod = .week

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 25) {
                    // Period Selector
                    Picker("Period", selection: $selectedPeriod) {
                        ForEach(TimePeriod.allCases, id: \.self) { period in
                            Text(period.displayName).tag(period)
                        }
                    }
                    .pickerStyle(.segmented)
                    .padding(.horizontal)

                    // Overview Stats
                    OverviewStatsView(
                        completedTasks: completedTasksCount,
                        totalTasks: allTasks.count,
                        focusTime: totalFocusTime,
                        productivity: productivityScore
                    )
                    .padding(.horizontal)

                    // Completion Chart
                    CompletionChartView(tasks: Array(allTasks), period: selectedPeriod)
                        .frame(height: 200)
                        .padding()
                        .background(Color.cardBackground)
                        .cornerRadius(15)
                        .padding(.horizontal)

                    // Category Breakdown
                    CategoryBreakdownView(tasks: Array(allTasks))
                        .padding()
                        .background(Color.cardBackground)
                        .cornerRadius(15)
                        .padding(.horizontal)

                    // Focus Sessions
                    FocusSessionsView(sessions: Array(focusSessions))
                        .padding()
                        .background(Color.cardBackground)
                        .cornerRadius(15)
                        .padding(.horizontal)

                    // Task Completion Rate
                    CompletionRateView(
                        completed: completedTasksCount,
                        total: allTasks.count
                    )
                    .padding()
                    .background(Color.cardBackground)
                    .cornerRadius(15)
                    .padding(.horizontal)
                }
                .padding(.vertical)
            }
            .navigationTitle("Analitik")
        }
    }

    private var completedTasksCount: Int {
        allTasks.filter { $0.isCompleted }.count
    }

    private var totalFocusTime: Int {
        focusSessions.reduce(0) { $0 + Int($1.duration) }
    }

    private var productivityScore: Double {
        guard allTasks.count > 0 else { return 0 }
        return Double(completedTasksCount) / Double(allTasks.count) * 100
    }

    enum TimePeriod: String, CaseIterable {
        case day = "Gün"
        case week = "Hafta"
        case month = "Ay"

        var displayName: String { rawValue }
    }
}

struct OverviewStatsView: View {
    let completedTasks: Int
    let totalTasks: Int
    let focusTime: Int
    let productivity: Double

    var body: some View {
        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())], spacing: 15) {
            StatBox(
                title: "Tamamlanan",
                value: "\(completedTasks)/\(totalTasks)",
                icon: "checkmark.circle.fill",
                color: .green
            )

            StatBox(
                title: "Odaklanma",
                value: "\(focusTime / 60)sa",
                icon: "timer",
                color: .blue
            )

            StatBox(
                title: "Verimlilik",
                value: String(format: "%.0f%%", productivity),
                icon: "chart.line.uptrend.xyaxis",
                color: .orange
            )

            StatBox(
                title: "Seri",
                value: "7 gün",
                icon: "flame.fill",
                color: .red
            )
        }
    }
}

struct StatBox: View {
    let title: String
    let value: String
    let icon: String
    let color: Color

    var body: some View {
        VStack(spacing: 10) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(color)

            Text(value)
                .font(.title2)
                .fontWeight(.bold)

            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color.cardBackground)
        .cornerRadius(12)
    }
}

struct CompletionChartView: View {
    let tasks: [Task]
    let period: AnalyticsView.TimePeriod

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Görev Tamamlama Trendi")
                .font(.headline)

            // Simplified chart representation
            HStack(alignment: .bottom, spacing: 8) {
                ForEach(0..<7, id: \.self) { index in
                    VStack {
                        Rectangle()
                            .fill(Color.blue)
                            .frame(height: CGFloat.random(in: 20...150))

                        Text("\(index + 1)")
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                }
            }
        }
    }
}

struct CategoryBreakdownView: View {
    let tasks: [Task]

    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Kategorilere Göre Dağılım")
                .font(.headline)

            ForEach(categoryStats, id: \.name) { stat in
                HStack {
                    Circle()
                        .fill(stat.color)
                        .frame(width: 12, height: 12)

                    Text(stat.name)
                        .font(.subheadline)

                    Spacer()

                    Text("\(stat.count)")
                        .font(.subheadline)
                        .fontWeight(.semibold)
                }
            }
        }
    }

    private var categoryStats: [(name: String, count: Int, color: Color)] {
        let grouped = Dictionary(grouping: tasks) { $0.category?.wrappedName ?? "Diğer" }
        return grouped.map { (name: $0.key, count: $0.value.count, color: .blue) }
            .sorted { $0.count > $1.count }
    }
}

struct FocusSessionsView: View {
    let sessions: [FocusSession]

    var body: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text("Odaklanma Oturumları")
                .font(.headline)

            HStack(spacing: 30) {
                VStack {
                    Text("\(sessions.count)")
                        .font(.title2)
                        .fontWeight(.bold)
                    Text("Toplam")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                VStack {
                    Text("\(totalFocusMinutes)")
                        .font(.title2)
                        .fontWeight(.bold)
                    Text("Dakika")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                VStack {
                    Text("\(sessions.filter { $0.isCompleted }.count)")
                        .font(.title2)
                        .fontWeight(.bold)
                    Text("Tamamlandı")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
    }

    private var totalFocusMinutes: Int {
        sessions.reduce(0) { $0 + Int($1.duration) / 60 }
    }
}

struct CompletionRateView: View {
    let completed: Int
    let total: Int

    private var percentage: Double {
        guard total > 0 else { return 0 }
        return Double(completed) / Double(total)
    }

    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            Text("Tamamlanma Oranı")
                .font(.headline)

            ZStack(alignment: .leading) {
                RoundedRectangle(cornerRadius: 10)
                    .fill(Color.gray.opacity(0.2))
                    .frame(height: 20)

                RoundedRectangle(cornerRadius: 10)
                    .fill(LinearGradient(
                        colors: [.green, .blue],
                        startPoint: .leading,
                        endPoint: .trailing
                    ))
                    .frame(width: UIScreen.main.bounds.width * 0.8 * percentage, height: 20)
            }

            Text("\(completed)/\(total) görev tamamlandı (\(Int(percentage * 100))%)")
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
    }
}
