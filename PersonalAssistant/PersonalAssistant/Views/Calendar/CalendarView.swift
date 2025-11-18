//
//  CalendarView.swift
//  PersonalAssistant
//
//  Calendar view with EventKit integration
//

import SwiftUI
import EventKit

struct CalendarView: View {
    @EnvironmentObject var calendarManager: CalendarManager
    @State private var selectedDate = Date()
    @State private var showingAddEvent = false

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Month Calendar
                MonthCalendarView(selectedDate: $selectedDate)
                    .padding()

                Divider()

                // Events for selected date
                List {
                    ForEach(eventsForSelectedDate, id: \.eventIdentifier) { event in
                        EventRowView(event: event)
                    }
                }
                .listStyle(.plain)
            }
            .navigationTitle("Takvim")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showingAddEvent = true }) {
                        Image(systemName: "plus.circle.fill")
                    }
                }
            }
            .sheet(isPresented: $showingAddEvent) {
                AddEventView(selectedDate: selectedDate)
            }
            .onAppear {
                calendarManager.loadUpcomingEvents()
            }
        }
    }

    private var eventsForSelectedDate: [EKEvent] {
        calendarManager.getEvents(for: selectedDate)
    }
}

struct MonthCalendarView: View {
    @Binding var selectedDate: Date

    private let calendar = Calendar.current
    private let daysOfWeek = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]

    var body: some View {
        VStack(spacing: 15) {
            // Month/Year header
            HStack {
                Button(action: previousMonth) {
                    Image(systemName: "chevron.left")
                }

                Spacer()

                Text(monthYearString)
                    .font(.headline)

                Spacer()

                Button(action: nextMonth) {
                    Image(systemName: "chevron.right")
                }
            }

            // Days of week
            HStack(spacing: 0) {
                ForEach(daysOfWeek, id: \.self) { day in
                    Text(day)
                        .font(.caption)
                        .fontWeight(.semibold)
                        .frame(maxWidth: .infinity)
                }
            }

            // Calendar grid
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 7), spacing: 8) {
                ForEach(daysInMonth, id: \.self) { date in
                    if let date = date {
                        DayCell(date: date, isSelected: calendar.isDate(date, inSameDayAs: selectedDate))
                            .onTapGesture {
                                selectedDate = date
                                HapticManager.shared.selection()
                            }
                    } else {
                        Color.clear
                            .frame(height: 40)
                    }
                }
            }
        }
    }

    private var monthYearString: String {
        let formatter = DateFormatter()
        formatter.dateFormat = "MMMM yyyy"
        formatter.locale = Locale(identifier: "tr_TR")
        return formatter.string(from: selectedDate)
    }

    private var daysInMonth: [Date?] {
        guard let monthInterval = calendar.dateInterval(of: .month, for: selectedDate),
              let monthFirstWeek = calendar.dateInterval(of: .weekOfMonth, for: monthInterval.start) else {
            return []
        }

        let days = calendar.generateDates(
            inside: monthInterval,
            matching: DateComponents(hour: 0, minute: 0, second: 0)
        )

        let firstDayOfMonth = monthInterval.start
        let weekday = calendar.component(.weekday, from: firstDayOfMonth)
        let emptyDays = (weekday == 1 ? 6 : weekday - 2)

        return Array(repeating: nil, count: emptyDays) + days
    }

    private func previousMonth() {
        selectedDate = calendar.date(byAdding: .month, value: -1, to: selectedDate) ?? selectedDate
    }

    private func nextMonth() {
        selectedDate = calendar.date(byAdding: .month, value: 1, to: selectedDate) ?? selectedDate
    }
}

struct DayCell: View {
    let date: Date
    let isSelected: Bool

    var body: some View {
        Text("\(Calendar.current.component(.day, from: date))")
            .font(.subheadline)
            .frame(maxWidth: .infinity)
            .frame(height: 40)
            .background(isSelected ? Color.blue : Color.clear)
            .foregroundColor(isSelected ? .white : .primary)
            .cornerRadius(8)
    }
}

struct EventRowView: View {
    let event: EKEvent

    var body: some View {
        HStack(spacing: 12) {
            Rectangle()
                .fill(event.calendar.cgColor.toColor())
                .frame(width: 4)

            VStack(alignment: .leading, spacing: 4) {
                Text(event.title ?? "Untitled")
                    .font(.subheadline)
                    .fontWeight(.medium)

                Text(formatEventTime())
                    .font(.caption)
                    .foregroundColor(.secondary)

                if let location = event.location {
                    HStack(spacing: 4) {
                        Image(systemName: "mappin.circle")
                        Text(location)
                    }
                    .font(.caption)
                    .foregroundColor(.secondary)
                }
            }

            Spacer()
        }
        .padding(.vertical, 8)
    }

    private func formatEventTime() -> String {
        let formatter = DateFormatter()
        formatter.timeStyle = .short

        if event.isAllDay {
            return "Tüm gün"
        } else {
            return "\(formatter.string(from: event.startDate)) - \(formatter.string(from: event.endDate))"
        }
    }
}

struct AddEventView: View {
    let selectedDate: Date
    @EnvironmentObject var calendarManager: CalendarManager
    @Environment(\.dismiss) private var dismiss

    @State private var title = ""
    @State private var startDate: Date
    @State private var endDate: Date
    @State private var location = ""
    @State private var notes = ""

    init(selectedDate: Date) {
        self.selectedDate = selectedDate
        _startDate = State(initialValue: selectedDate)
        _endDate = State(initialValue: selectedDate.addingTimeInterval(3600))
    }

    var body: some View {
        NavigationView {
            Form {
                TextField("Başlık", text: $title)

                DatePicker("Başlangıç", selection: $startDate)
                DatePicker("Bitiş", selection: $endDate)

                TextField("Konum", text: $location)

                Section("Notlar") {
                    TextEditor(text: $notes)
                        .frame(minHeight: 80)
                }
            }
            .navigationTitle("Yeni Etkinlik")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("İptal") { dismiss() }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button("Ekle") {
                        addEvent()
                    }
                    .disabled(title.isEmpty)
                }
            }
        }
    }

    private func addEvent() {
        do {
            _ = try calendarManager.createEvent(
                title: title,
                startDate: startDate,
                endDate: endDate,
                notes: notes.isEmpty ? nil : notes,
                location: location.isEmpty ? nil : location
            )
            HapticManager.shared.success()
            dismiss()
        } catch {
            print("Error creating event: \(error)")
        }
    }
}

// Calendar extension for date generation
extension Calendar {
    func generateDates(inside interval: DateInterval, matching components: DateComponents) -> [Date] {
        var dates: [Date] = []
        dates.append(interval.start)

        enumerateDates(
            startingAfter: interval.start,
            matching: components,
            matchingPolicy: .nextTime
        ) { date, _, stop in
            if let date = date {
                if date < interval.end {
                    dates.append(date)
                } else {
                    stop = true
                }
            }
        }

        return dates
    }
}
