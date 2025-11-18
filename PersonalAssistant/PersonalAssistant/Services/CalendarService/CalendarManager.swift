//
//  CalendarManager.swift
//  PersonalAssistant
//
//  Manages EventKit calendar integration
//

import Foundation
import EventKit
import Combine

@MainActor
class CalendarManager: ObservableObject {
    static let shared = CalendarManager()

    @Published var hasAccess = false
    @Published var calendars: [EKCalendar] = []
    @Published var upcomingEvents: [EKEvent] = []
    @Published var todayEvents: [EKEvent] = []

    private let eventStore = EKEventStore()
    private var cancellables = Set<AnyCancellable>()

    init() {
        checkAccess()
        setupNotifications()
    }

    // MARK: - Authorization

    func checkAccess() {
        let status = EKEventStore.authorizationStatus(for: .event)
        hasAccess = (status == .authorized)
    }

    func requestAccess() async -> Bool {
        do {
            let granted = try await eventStore.requestAccess(to: .event)
            await MainActor.run {
                hasAccess = granted
                if granted {
                    loadCalendars()
                    loadUpcomingEvents()
                }
            }
            return granted
        } catch {
            print("Error requesting calendar access: \(error)")
            return false
        }
    }

    // MARK: - Load Data

    func loadCalendars() {
        calendars = eventStore.calendars(for: .event)
    }

    func loadUpcomingEvents(daysAhead: Int = 7) {
        guard hasAccess else { return }

        let startDate = Date()
        let endDate = Calendar.current.date(byAdding: .day, value: daysAhead, to: startDate)!

        let predicate = eventStore.predicateForEvents(
            withStart: startDate,
            end: endDate,
            calendars: nil
        )

        upcomingEvents = eventStore.events(matching: predicate)
            .sorted { $0.startDate < $1.startDate }
    }

    func loadTodayEvents() {
        guard hasAccess else { return }

        let calendar = Calendar.current
        let startOfDay = calendar.startOfDay(for: Date())
        let endOfDay = calendar.date(byAdding: .day, value: 1, to: startOfDay)!

        let predicate = eventStore.predicateForEvents(
            withStart: startOfDay,
            end: endOfDay,
            calendars: nil
        )

        todayEvents = eventStore.events(matching: predicate)
            .sorted { $0.startDate < $1.startDate }
    }

    func getEvents(for date: Date) -> [EKEvent] {
        guard hasAccess else { return [] }

        let calendar = Calendar.current
        let startOfDay = calendar.startOfDay(for: date)
        let endOfDay = calendar.date(byAdding: .day, value: 1, to: startOfDay)!

        let predicate = eventStore.predicateForEvents(
            withStart: startOfDay,
            end: endOfDay,
            calendars: nil
        )

        return eventStore.events(matching: predicate)
            .sorted { $0.startDate < $1.startDate }
    }

    // MARK: - Event Management

    func createEvent(
        title: String,
        startDate: Date,
        endDate: Date,
        calendar: EKCalendar? = nil,
        notes: String? = nil,
        location: String? = nil,
        alarms: [EKAlarm] = []
    ) throws -> EKEvent {
        let event = EKEvent(eventStore: eventStore)
        event.title = title
        event.startDate = startDate
        event.endDate = endDate
        event.calendar = calendar ?? eventStore.defaultCalendarForNewEvents
        event.notes = notes
        event.location = location

        // Add alarms
        for alarm in alarms {
            event.addAlarm(alarm)
        }

        try eventStore.save(event, span: .thisEvent)
        loadUpcomingEvents()

        return event
    }

    func updateEvent(_ event: EKEvent) throws {
        try eventStore.save(event, span: .thisEvent)
        loadUpcomingEvents()
    }

    func deleteEvent(_ event: EKEvent) throws {
        try eventStore.remove(event, span: .thisEvent)
        loadUpcomingEvents()
    }

    // MARK: - Reminders for Events

    func getUpcomingEventsForNotifications(hoursAhead: Int = 24) -> [EKEvent] {
        guard hasAccess else { return [] }

        let startDate = Date()
        let endDate = Calendar.current.date(byAdding: .hour, value: hoursAhead, to: startDate)!

        let predicate = eventStore.predicateForEvents(
            withStart: startDate,
            end: endDate,
            calendars: nil
        )

        return eventStore.events(matching: predicate)
            .filter { event in
                // Check if event is within the next 24 hours
                let timeUntilEvent = event.startDate.timeIntervalSinceNow
                return timeUntilEvent > 0 && timeUntilEvent <= Double(hoursAhead * 3600)
            }
            .sorted { $0.startDate < $1.startDate }
    }

    func scheduleNotificationsForUpcomingEvents() async {
        let events = getUpcomingEventsForNotifications()

        for event in events {
            // Schedule notification 24 hours before
            let notificationDate = event.startDate.addingTimeInterval(-86400)

            if notificationDate > Date() {
                let body = createEventNotificationBody(for: event)

                try? await NotificationManager.shared.scheduleNotification(
                    id: event.eventIdentifier,
                    title: "Yarın: \(event.title ?? "")",
                    body: body,
                    date: notificationDate
                )
            }

            // Schedule notification 1 hour before
            let oneHourBefore = event.startDate.addingTimeInterval(-3600)
            if oneHourBefore > Date() {
                let body = createEventNotificationBody(for: event)

                try? await NotificationManager.shared.scheduleNotification(
                    id: "\(event.eventIdentifier)_1h",
                    title: "1 saat sonra: \(event.title ?? "")",
                    body: body,
                    date: oneHourBefore
                )
            }
        }
    }

    private func createEventNotificationBody(for event: EKEvent) -> String {
        var body = ""

        let formatter = DateFormatter()
        formatter.dateStyle = .short
        formatter.timeStyle = .short

        body += formatter.string(from: event.startDate)

        if let location = event.location {
            body += "\n📍 \(location)"
        }

        if let attendees = event.attendees, !attendees.isEmpty {
            body += "\n👥 \(attendees.count) katılımcı"
        }

        return body
    }

    // MARK: - Calendar Selection

    func getSelectableCalendars() -> [EKCalendar] {
        return calendars.filter { $0.allowsContentModifications }
    }

    // MARK: - Notifications

    private func setupNotifications() {
        NotificationCenter.default.publisher(for: .EKEventStoreChanged)
            .sink { [weak self] _ in
                Task { @MainActor in
                    self?.loadUpcomingEvents()
                    self?.loadTodayEvents()
                }
            }
            .store(in: &cancellables)
    }

    // MARK: - Helper Methods

    func formatEventTime(_ event: EKEvent) -> String {
        let formatter = DateFormatter()
        formatter.timeStyle = .short

        if event.isAllDay {
            return "Tüm gün"
        } else {
            let start = formatter.string(from: event.startDate)
            let end = formatter.string(from: event.endDate)
            return "\(start) - \(end)"
        }
    }

    func isEventToday(_ event: EKEvent) -> Bool {
        return Calendar.current.isDateInToday(event.startDate)
    }

    func isEventTomorrow(_ event: EKEvent) -> Bool {
        return Calendar.current.isDateInTomorrow(event.startDate)
    }

    func timeUntilEvent(_ event: EKEvent) -> String {
        let interval = event.startDate.timeIntervalSinceNow

        if interval < 0 {
            return "Şimdi"
        }

        let hours = Int(interval / 3600)
        let minutes = Int((interval.truncatingRemainder(dividingBy: 3600)) / 60)

        if hours > 24 {
            let days = hours / 24
            return "\(days) gün sonra"
        } else if hours > 0 {
            return "\(hours) saat sonra"
        } else {
            return "\(minutes) dakika sonra"
        }
    }
}
