//
//  EventCardView.swift
//  PersonalAssistant
//
//  Compact card view for calendar events
//

import SwiftUI
import EventKit

struct EventCardView: View {
    let event: EKEvent
    @EnvironmentObject var calendarManager: CalendarManager

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Time
            HStack {
                Image(systemName: "clock")
                    .font(.caption)
                Text(calendarManager.formatEventTime(event))
                    .font(.caption)
                    .fontWeight(.medium)
            }
            .foregroundColor(event.calendar.cgColor.toColor())

            // Title
            Text(event.title ?? "Untitled")
                .font(.subheadline)
                .fontWeight(.semibold)
                .lineLimit(2)

            // Location
            if let location = event.location, !location.isEmpty {
                HStack(spacing: 4) {
                    Image(systemName: "mappin.circle.fill")
                        .font(.caption2)
                    Text(location)
                        .font(.caption2)
                        .lineLimit(1)
                }
                .foregroundColor(.secondary)
            }

            // Attendees
            if let attendees = event.attendees, !attendees.isEmpty {
                HStack(spacing: 4) {
                    Image(systemName: "person.2.fill")
                        .font(.caption2)
                    Text("\(attendees.count) katılımcı")
                        .font(.caption2)
                }
                .foregroundColor(.secondary)
            }
        }
        .padding()
        .frame(width: 200)
        .background(Color.cardBackground)
        .cornerRadius(15)
        .shadow(color: .black.opacity(0.05), radius: 5, x: 0, y: 2)
    }
}

extension CGColor {
    func toColor() -> Color {
        return Color(cgColor: self)
    }
}
