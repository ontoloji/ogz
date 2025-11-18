//
//  PersonalAssistantWidget.swift
//  PersonalAssistantWidget
//
//  Widget for Personal Assistant app
//

import WidgetKit
import SwiftUI

struct Provider: TimelineProvider {
    func placeholder(in context: Context) -> SimpleEntry {
        SimpleEntry(date: Date(), tasks: [], todayEvents: 0)
    }

    func getSnapshot(in context: Context, completion: @escaping (SimpleEntry) -> ()) {
        let entry = SimpleEntry(date: Date(), tasks: sampleTasks, todayEvents: 3)
        completion(entry)
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<Entry>) -> ()) {
        var entries: [SimpleEntry] = []

        // Fetch tasks from CoreData
        let tasks = fetchTodayTasks()
        let eventsCount = fetchTodayEventsCount()

        let currentDate = Date()
        for hourOffset in 0 ..< 5 {
            let entryDate = Calendar.current.date(byAdding: .hour, value: hourOffset, to: currentDate)!
            let entry = SimpleEntry(date: entryDate, tasks: tasks, todayEvents: eventsCount)
            entries.append(entry)
        }

        let timeline = Timeline(entries: entries, policy: .atEnd)
        completion(timeline)
    }

    private func fetchTodayTasks() -> [TaskItem] {
        // In a real implementation, fetch from shared Core Data container
        return sampleTasks
    }

    private func fetchTodayEventsCount() -> Int {
        // In a real implementation, fetch from EventKit
        return 2
    }

    private var sampleTasks: [TaskItem] {
        [
            TaskItem(id: UUID(), title: "Toplantıya katıl", isCompleted: false, priority: 2),
            TaskItem(id: UUID(), title: "Rapor hazırla", isCompleted: false, priority: 1),
            TaskItem(id: UUID(), title: "E-postaları kontrol et", isCompleted: true, priority: 0)
        ]
    }
}

struct SimpleEntry: TimelineEntry {
    let date: Date
    let tasks: [TaskItem]
    let todayEvents: Int
}

struct TaskItem: Identifiable {
    let id: UUID
    let title: String
    let isCompleted: Bool
    let priority: Int
}

struct PersonalAssistantWidgetEntryView : View {
    var entry: Provider.Entry
    @Environment(\.widgetFamily) var widgetFamily

    var body: some View {
        switch widgetFamily {
        case .systemSmall:
            SmallWidgetView(entry: entry)
        case .systemMedium:
            MediumWidgetView(entry: entry)
        case .systemLarge:
            LargeWidgetView(entry: entry)
        case .accessoryCircular:
            AccessoryCircularView(entry: entry)
        case .accessoryRectangular:
            AccessoryRectangularView(entry: entry)
        case .accessoryInline:
            AccessoryInlineView(entry: entry)
        @unknown default:
            SmallWidgetView(entry: entry)
        }
    }
}

// MARK: - Small Widget
struct SmallWidgetView: View {
    let entry: Provider.Entry

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Image(systemName: "checkmark.circle.fill")
                    .foregroundColor(.blue)
                Text("Bugün")
                    .font(.caption)
                    .fontWeight(.semibold)
            }

            Spacer()

            VStack(alignment: .leading, spacing: 4) {
                Text("\(incompleteTasks)")
                    .font(.system(size: 36, weight: .bold))
                Text("görev kaldı")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            if entry.todayEvents > 0 {
                HStack(spacing: 4) {
                    Image(systemName: "calendar")
                        .font(.caption2)
                    Text("\(entry.todayEvents) etkinlik")
                        .font(.caption2)
                }
                .foregroundColor(.secondary)
            }
        }
        .padding()
    }

    private var incompleteTasks: Int {
        entry.tasks.filter { !$0.isCompleted }.count
    }
}

// MARK: - Medium Widget
struct MediumWidgetView: View {
    let entry: Provider.Entry

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Image(systemName: "checkmark.circle.fill")
                    .foregroundColor(.blue)
                Text("Bugünkü Görevler")
                    .font(.subheadline)
                    .fontWeight(.semibold)
                Spacer()
                Text("\(incompleteTasks)/\(entry.tasks.count)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            ForEach(entry.tasks.prefix(3)) { task in
                HStack(spacing: 8) {
                    Image(systemName: task.isCompleted ? "checkmark.circle.fill" : "circle")
                        .foregroundColor(task.isCompleted ? .green : .gray)
                        .font(.caption)

                    Text(task.title)
                        .font(.caption)
                        .strikethrough(task.isCompleted)
                        .foregroundColor(task.isCompleted ? .secondary : .primary)
                        .lineLimit(1)

                    Spacer()

                    if task.priority > 0 {
                        Circle()
                            .fill(task.priority == 2 ? Color.red : Color.orange)
                            .frame(width: 6, height: 6)
                    }
                }
            }

            if entry.tasks.count > 3 {
                Text("+\(entry.tasks.count - 3) daha fazla görev")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
    }

    private var incompleteTasks: Int {
        entry.tasks.filter { !$0.isCompleted }.count
    }
}

// MARK: - Large Widget
struct LargeWidgetView: View {
    let entry: Provider.Entry

    var body: some View {
        VStack(alignment: .leading, spacing: 15) {
            // Header
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("Personal Assistant")
                        .font(.headline)
                    Text(entry.date, style: .date)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }

                Spacer()

                VStack(alignment: .trailing, spacing: 4) {
                    Text("\(incompleteTasks)")
                        .font(.title2)
                        .fontWeight(.bold)
                    Text("görev kaldı")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }

            Divider()

            // Tasks List
            VStack(alignment: .leading, spacing: 10) {
                Text("Bugünkü Görevler")
                    .font(.subheadline)
                    .fontWeight(.semibold)

                ForEach(entry.tasks) { task in
                    HStack(spacing: 10) {
                        Image(systemName: task.isCompleted ? "checkmark.circle.fill" : "circle")
                            .foregroundColor(task.isCompleted ? .green : .gray)

                        Text(task.title)
                            .font(.caption)
                            .strikethrough(task.isCompleted)
                            .foregroundColor(task.isCompleted ? .secondary : .primary)
                            .lineLimit(1)

                        Spacer()

                        if task.priority > 0 {
                            Image(systemName: "flag.fill")
                                .font(.caption2)
                                .foregroundColor(task.priority == 2 ? .red : .orange)
                        }
                    }
                }
            }

            Spacer()

            // Stats
            if entry.todayEvents > 0 {
                HStack {
                    Image(systemName: "calendar")
                    Text("\(entry.todayEvents) etkinlik bugün")
                        .font(.caption)
                }
                .foregroundColor(.secondary)
            }
        }
        .padding()
    }

    private var incompleteTasks: Int {
        entry.tasks.filter { !$0.isCompleted }.count
    }
}

// MARK: - Lock Screen Widgets (iOS 16+)

struct AccessoryCircularView: View {
    let entry: Provider.Entry

    var body: some View {
        ZStack {
            AccessoryWidgetBackground()

            VStack(spacing: 2) {
                Text("\(incompleteTasks)")
                    .font(.title2)
                    .fontWeight(.bold)
                Text("görev")
                    .font(.caption2)
            }
        }
    }

    private var incompleteTasks: Int {
        entry.tasks.filter { !$0.isCompleted }.count
    }
}

struct AccessoryRectangularView: View {
    let entry: Provider.Entry

    var body: some View {
        VStack(alignment: .leading, spacing: 4) {
            HStack {
                Image(systemName: "checkmark.circle")
                Text("Görevler")
                    .font(.caption)
                    .fontWeight(.semibold)
            }

            Text("\(incompleteTasks) görev kaldı")
                .font(.caption2)
                .foregroundColor(.secondary)

            if entry.todayEvents > 0 {
                Text("\(entry.todayEvents) etkinlik")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
    }

    private var incompleteTasks: Int {
        entry.tasks.filter { !$0.isCompleted }.count
    }
}

struct AccessoryInlineView: View {
    let entry: Provider.Entry

    var body: some View {
        Text("\(incompleteTasks) görev, \(entry.todayEvents) etkinlik")
    }

    private var incompleteTasks: Int {
        entry.tasks.filter { !$0.isCompleted }.count
    }
}

// MARK: - Widget Configuration

@main
struct PersonalAssistantWidget: Widget {
    let kind: String = "PersonalAssistantWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: Provider()) { entry in
            PersonalAssistantWidgetEntryView(entry: entry)
        }
        .configurationDisplayName("Personal Assistant")
        .description("Bugünkü görevlerini ve etkinliklerini takip et")
        .supportedFamilies([
            .systemSmall,
            .systemMedium,
            .systemLarge,
            .accessoryCircular,
            .accessoryRectangular,
            .accessoryInline
        ])
    }
}

// MARK: - Preview

struct PersonalAssistantWidget_Previews: PreviewProvider {
    static var previews: some View {
        PersonalAssistantWidgetEntryView(entry: SimpleEntry(
            date: Date(),
            tasks: [
                TaskItem(id: UUID(), title: "Toplantıya katıl", isCompleted: false, priority: 2),
                TaskItem(id: UUID(), title: "Rapor hazırla", isCompleted: false, priority: 1),
                TaskItem(id: UUID(), title: "E-postaları kontrol et", isCompleted: true, priority: 0)
            ],
            todayEvents: 3
        ))
        .previewContext(WidgetPreviewContext(family: .systemMedium))
    }
}
