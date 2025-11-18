//
//  NotificationManager.swift
//  PersonalAssistant
//
//  Manages local notifications and reminders
//

import Foundation
import UserNotifications
import CoreLocation

@MainActor
class NotificationManager: NSObject, ObservableObject {
    static let shared = NotificationManager()

    @Published var isAuthorized = false
    @Published var authorizationStatus: UNAuthorizationStatus = .notDetermined

    private let notificationCenter = UNUserNotificationCenter.current()

    override init() {
        super.init()
        notificationCenter.delegate = self
        checkAuthorizationStatus()
    }

    // MARK: - Authorization

    func checkAuthorizationStatus() {
        Task {
            let settings = await notificationCenter.notificationSettings()
            authorizationStatus = settings.authorizationStatus
            isAuthorized = settings.authorizationStatus == .authorized
        }
    }

    func requestAuthorization() async -> Bool {
        do {
            let granted = try await notificationCenter.requestAuthorization(
                options: [.alert, .badge, .sound, .criticalAlert]
            )
            await MainActor.run {
                isAuthorized = granted
                authorizationStatus = granted ? .authorized : .denied
            }
            return granted
        } catch {
            print("Error requesting notification authorization: \(error)")
            return false
        }
    }

    // MARK: - Schedule Notifications

    func scheduleNotification(
        id: String,
        title: String,
        body: String,
        date: Date,
        repeats: Bool = false,
        repeatInterval: RepeatInterval? = nil,
        categoryIdentifier: String? = nil
    ) async throws {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        content.badge = 1

        if let categoryIdentifier = categoryIdentifier {
            content.categoryIdentifier = categoryIdentifier
        }

        // Add actions
        content.userInfo = ["noteID": id]

        var trigger: UNNotificationTrigger?

        if let repeatInterval = repeatInterval, repeats {
            trigger = createRepeatTrigger(for: date, interval: repeatInterval)
        } else {
            let components = Calendar.current.dateComponents(
                [.year, .month, .day, .hour, .minute],
                from: date
            )
            trigger = UNCalendarNotificationTrigger(dateMatching: components, repeats: false)
        }

        let request = UNNotificationRequest(
            identifier: id,
            content: content,
            trigger: trigger
        )

        try await notificationCenter.add(request)
    }

    // MARK: - Location-based Notifications

    func scheduleLocationNotification(
        id: String,
        title: String,
        body: String,
        coordinate: CLLocationCoordinate2D,
        radius: CLLocationDistance = 100,
        notifyOnEntry: Bool = true,
        notifyOnExit: Bool = false
    ) async throws {
        let content = UNMutableNotificationContent()
        content.title = title
        content.body = body
        content.sound = .default
        content.badge = 1
        content.userInfo = ["noteID": id]

        let region = CLCircularRegion(
            center: coordinate,
            radius: radius,
            identifier: id
        )
        region.notifyOnEntry = notifyOnEntry
        region.notifyOnExit = notifyOnExit

        let trigger = UNLocationNotificationTrigger(region: region, repeats: false)

        let request = UNNotificationRequest(
            identifier: id,
            content: content,
            trigger: trigger
        )

        try await notificationCenter.add(request)
    }

    // MARK: - Cancel Notifications

    func cancelNotification(id: String) {
        notificationCenter.removePendingNotificationRequests(withIdentifiers: [id])
        notificationCenter.removeDeliveredNotifications(withIdentifiers: [id])
    }

    func cancelAllNotifications() {
        notificationCenter.removeAllPendingNotificationRequests()
        notificationCenter.removeAllDeliveredNotifications()
    }

    // MARK: - Scheduled Notifications

    func schedulePendingNotifications() async {
        // This method is called on app launch to reschedule any missed notifications
        let pendingRequests = await notificationCenter.pendingNotificationRequests()
        print("Pending notifications: \(pendingRequests.count)")
    }

    func getPendingNotifications() async -> [UNNotificationRequest] {
        return await notificationCenter.pendingNotificationRequests()
    }

    // MARK: - Helper Methods

    private func createRepeatTrigger(for date: Date, interval: RepeatInterval) -> UNCalendarNotificationTrigger {
        var components: DateComponents

        switch interval {
        case .daily:
            components = Calendar.current.dateComponents([.hour, .minute], from: date)
        case .weekly:
            components = Calendar.current.dateComponents([.weekday, .hour, .minute], from: date)
        case .monthly:
            components = Calendar.current.dateComponents([.day, .hour, .minute], from: date)
        case .yearly:
            components = Calendar.current.dateComponents([.month, .day, .hour, .minute], from: date)
        }

        return UNCalendarNotificationTrigger(dateMatching: components, repeats: true)
    }

    // MARK: - Notification Categories

    func setupNotificationCategories() {
        let completeAction = UNNotificationAction(
            identifier: "COMPLETE_ACTION",
            title: "Tamamlandı olarak işaretle",
            options: .foreground
        )

        let snoozeAction = UNNotificationAction(
            identifier: "SNOOZE_ACTION",
            title: "Ertele (10 dk)",
            options: []
        )

        let deleteAction = UNNotificationAction(
            identifier: "DELETE_ACTION",
            title: "Sil",
            options: .destructive
        )

        let reminderCategory = UNNotificationCategory(
            identifier: "REMINDER",
            actions: [completeAction, snoozeAction, deleteAction],
            intentIdentifiers: [],
            options: .customDismissAction
        )

        notificationCenter.setNotificationCategories([reminderCategory])
    }

    // Repeat intervals
    enum RepeatInterval: String, CaseIterable {
        case daily = "Günlük"
        case weekly = "Haftalık"
        case monthly = "Aylık"
        case yearly = "Yıllık"
    }
}

// MARK: - UNUserNotificationCenterDelegate

extension NotificationManager: UNUserNotificationCenterDelegate {
    // Handle notification when app is in foreground
    nonisolated func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        completionHandler([.banner, .sound, .badge])
    }

    // Handle notification response
    nonisolated func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        let userInfo = response.notification.request.content.userInfo

        switch response.actionIdentifier {
        case "COMPLETE_ACTION":
            print("Complete action tapped")
            // Handle completion

        case "SNOOZE_ACTION":
            print("Snooze action tapped")
            // Snooze for 10 minutes
            if let noteID = userInfo["noteID"] as? String {
                Task {
                    let snoozeDate = Date().addingTimeInterval(600) // 10 minutes
                    try? await NotificationManager.shared.scheduleNotification(
                        id: noteID,
                        title: response.notification.request.content.title,
                        body: response.notification.request.content.body,
                        date: snoozeDate
                    )
                }
            }

        case "DELETE_ACTION":
            print("Delete action tapped")
            // Handle deletion

        case UNNotificationDefaultActionIdentifier:
            print("Notification tapped")
            // Open the app to the relevant note/task

        default:
            break
        }

        completionHandler()
    }
}
