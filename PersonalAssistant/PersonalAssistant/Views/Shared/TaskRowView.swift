//
//  TaskRowView.swift
//  PersonalAssistant
//
//  Row view for tasks
//

import SwiftUI

struct TaskRowView: View {
    @ObservedObject var task: Task
    @Environment(\.managedObjectContext) private var viewContext

    var body: some View {
        HStack(spacing: 12) {
            // Completion button
            Button(action: {
                toggleCompletion()
            }) {
                Image(systemName: task.isCompleted ? "checkmark.circle.fill" : "circle")
                    .font(.title3)
                    .foregroundColor(task.isCompleted ? .green : .gray)
            }
            .buttonStyle(.plain)

            VStack(alignment: .leading, spacing: 4) {
                // Title
                Text(task.wrappedTitle)
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .strikethrough(task.isCompleted)
                    .foregroundColor(task.isCompleted ? .secondary : .primary)

                // Metadata
                HStack(spacing: 12) {
                    // Due date
                    if let dueDate = task.dueDate {
                        HStack(spacing: 4) {
                            Image(systemName: "calendar")
                            Text(formatDueDate(dueDate))
                        }
                        .font(.caption)
                        .foregroundColor(task.isOverdue ? .red : .secondary)
                    }

                    // Priority
                    if task.priority > 0 {
                        HStack(spacing: 2) {
                            Image(systemName: task.priorityLevel.icon)
                            Text(task.priorityLevel.displayName)
                        }
                        .font(.caption)
                        .foregroundColor(task.priorityLevel.color)
                    }

                    // Category
                    if let category = task.category {
                        Text(category.wrappedName)
                            .font(.caption)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(category.categoryColor.opacity(0.2))
                            .foregroundColor(category.categoryColor)
                            .cornerRadius(4)
                    }
                }
            }

            Spacer()

            // Subtasks indicator
            if !task.subtasksArray.isEmpty {
                VStack(alignment: .trailing, spacing: 2) {
                    Text("\(task.subtasksArray.filter { $0.isCompleted }.count)/\(task.subtasksArray.count)")
                        .font(.caption2)
                        .fontWeight(.medium)
                    ProgressView(value: task.completionPercentage)
                        .frame(width: 40)
                }
            }
        }
        .padding()
        .background(Color.cardBackground)
        .cornerRadius(12)
    }

    private func toggleCompletion() {
        withAnimation {
            task.toggleCompletion()
            do {
                try viewContext.save()
                HapticManager.shared.success()
            } catch {
                print("Error toggling task: \(error)")
            }
        }
    }

    private func formatDueDate(_ date: Date) -> String {
        let calendar = Calendar.current

        if calendar.isDateInToday(date) {
            return "Bugün"
        } else if calendar.isDateInTomorrow(date) {
            return "Yarın"
        } else if calendar.isDateInYesterday(date) {
            return "Dün"
        } else {
            let formatter = DateFormatter()
            formatter.dateFormat = "d MMM"
            return formatter.string(from: date)
        }
    }
}
