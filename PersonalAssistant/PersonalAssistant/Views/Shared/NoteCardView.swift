//
//  NoteCardView.swift
//  PersonalAssistant
//
//  Card view for notes
//

import SwiftUI

struct NoteCardView: View {
    @ObservedObject var note: Note

    var body: some View {
        NavigationLink(destination: NoteDetailView(note: note)) {
            VStack(alignment: .leading, spacing: 8) {
                // Header with category
                HStack {
                    if let category = note.category {
                        HStack(spacing: 4) {
                            Image(systemName: category.wrappedIconName)
                            Text(category.wrappedName)
                        }
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(category.categoryColor.opacity(0.2))
                        .foregroundColor(category.categoryColor)
                        .cornerRadius(6)
                    }

                    Spacer()

                    // Priority indicator
                    if note.priority > 0 {
                        Image(systemName: note.priorityLevel.icon)
                            .font(.caption)
                            .foregroundColor(note.priorityLevel.color)
                    }

                    // Pin indicator
                    if note.isPinned {
                        Image(systemName: "pin.fill")
                            .font(.caption)
                            .foregroundColor(.orange)
                    }
                }

                // Title
                Text(note.wrappedTitle)
                    .font(.headline)
                    .fontWeight(.semibold)
                    .lineLimit(2)
                    .foregroundColor(.primary)

                // Content preview
                if !note.wrappedContent.isEmpty {
                    Text(note.wrappedContent)
                        .font(.subheadline)
                        .foregroundColor(.secondary)
                        .lineLimit(3)
                }

                // Footer
                HStack {
                    // Reminder indicator
                    if note.hasReminder, let reminder = note.nextReminder {
                        HStack(spacing: 4) {
                            Image(systemName: "bell.fill")
                            Text(formatReminderDate(reminder.date ?? Date()))
                        }
                        .font(.caption2)
                        .foregroundColor(.orange)
                    }

                    Spacer()

                    // Modified date
                    Text(formatDate(note.modifiedAt ?? Date()))
                        .font(.caption2)
                        .foregroundColor(.secondary)
                }
            }
            .padding()
            .background(note.categoryColor.opacity(0.05))
            .overlay(
                RoundedRectangle(cornerRadius: 12)
                    .stroke(note.categoryColor.opacity(0.3), lineWidth: 1)
            )
            .cornerRadius(12)
        }
        .buttonStyle(.plain)
    }

    private func formatDate(_ date: Date) -> String {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .short
        return formatter.localizedString(for: date, relativeTo: Date())
    }

    private func formatReminderDate(_ date: Date) -> String {
        let calendar = Calendar.current

        if calendar.isDateInToday(date) {
            let formatter = DateFormatter()
            formatter.timeStyle = .short
            return formatter.string(from: date)
        } else if calendar.isDateInTomorrow(date) {
            return "Yarın"
        } else {
            let formatter = DateFormatter()
            formatter.dateFormat = "d MMM"
            return formatter.string(from: date)
        }
    }
}
