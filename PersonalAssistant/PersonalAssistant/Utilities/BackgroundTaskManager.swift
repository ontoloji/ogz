//
//  BackgroundTaskManager.swift
//  PersonalAssistant
//
//  Manages background tasks for app refresh and notifications
//

import Foundation
import BackgroundTasks
import UIKit

class BackgroundTaskManager {
    static let shared = BackgroundTaskManager()

    private let appRefreshTaskIdentifier = "com.personalassistant.app.refresh"
    private let databaseCleanupTaskIdentifier = "com.personalassistant.db.cleanup"

    private init() {}

    func registerBackgroundTasks() {
        // Register background app refresh
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: appRefreshTaskIdentifier,
            using: nil
        ) { task in
            self.handleAppRefresh(task: task as! BGAppRefreshTask)
        }

        // Register database cleanup
        BGTaskScheduler.shared.register(
            forTaskWithIdentifier: databaseCleanupTaskIdentifier,
            using: nil
        ) { task in
            self.handleDatabaseCleanup(task: task as! BGProcessingTask)
        }

        scheduleAppRefresh()
    }

    // MARK: - Schedule Tasks

    func scheduleAppRefresh() {
        let request = BGAppRefreshTaskRequest(identifier: appRefreshTaskIdentifier)
        request.earliestBeginDate = Date(timeIntervalSinceNow: 15 * 60) // 15 minutes

        do {
            try BGTaskScheduler.shared.submit(request)
            print("Background app refresh scheduled")
        } catch {
            print("Could not schedule app refresh: \(error)")
        }
    }

    func scheduleDatabaseCleanup() {
        let request = BGProcessingTaskRequest(identifier: databaseCleanupTaskIdentifier)
        request.requiresNetworkConnectivity = false
        request.requiresExternalPower = false
        request.earliestBeginDate = Date(timeIntervalSinceNow: 24 * 60 * 60) // 24 hours

        do {
            try BGTaskScheduler.shared.submit(request)
            print("Database cleanup scheduled")
        } catch {
            print("Could not schedule database cleanup: \(error)")
        }
    }

    // MARK: - Handle Tasks

    private func handleAppRefresh(task: BGAppRefreshTask) {
        // Schedule next refresh
        scheduleAppRefresh()

        let queue = OperationQueue()
        queue.maxConcurrentOperationCount = 1

        let operation = BlockOperation {
            // Sync with iCloud
            Task {
                await CloudKitManager.shared.syncWithCloud()
            }

            // Update notifications
            Task {
                await NotificationManager.shared.schedulePendingNotifications()
            }

            // Refresh calendar events
            Task {
                await CalendarManager.shared.loadUpcomingEvents()
                await CalendarManager.shared.scheduleNotificationsForUpcomingEvents()
            }
        }

        task.expirationHandler = {
            queue.cancelAllOperations()
        }

        operation.completionBlock = {
            task.setTaskCompleted(success: !operation.isCancelled)
        }

        queue.addOperation(operation)
    }

    private func handleDatabaseCleanup(task: BGProcessingTask) {
        // Schedule next cleanup
        scheduleDatabaseCleanup()

        let queue = OperationQueue()
        queue.maxConcurrentOperationCount = 1

        let operation = BlockOperation {
            // Clean up old completed tasks
            self.cleanupOldCompletedTasks()

            // Clean up old time entries
            self.cleanupOldTimeEntries()

            // Clean up expired reminders
            self.cleanupExpiredReminders()
        }

        task.expirationHandler = {
            queue.cancelAllOperations()
        }

        operation.completionBlock = {
            task.setTaskCompleted(success: !operation.isCancelled)
        }

        queue.addOperation(operation)
    }

    // MARK: - Cleanup Methods

    private func cleanupOldCompletedTasks() {
        let context = PersistenceController.shared.container.viewContext

        // Delete completed tasks older than 30 days
        let thirtyDaysAgo = Calendar.current.date(byAdding: .day, value: -30, to: Date())!

        let fetchRequest = Task.fetchRequest()
        fetchRequest.predicate = NSPredicate(
            format: "isCompleted == YES AND completedAt < %@",
            thirtyDaysAgo as NSDate
        )

        do {
            let tasks = try context.fetch(fetchRequest)
            for task in tasks {
                context.delete(task)
            }
            try context.save()
            print("Cleaned up \(tasks.count) old completed tasks")
        } catch {
            print("Error cleaning up tasks: \(error)")
        }
    }

    private func cleanupOldTimeEntries() {
        let context = PersistenceController.shared.container.viewContext

        // Delete time entries older than 90 days
        let ninetyDaysAgo = Calendar.current.date(byAdding: .day, value: -90, to: Date())!

        let fetchRequest = TimeEntry.fetchRequest()
        fetchRequest.predicate = NSPredicate(format: "startTime < %@", ninetyDaysAgo as NSDate)

        do {
            let entries = try context.fetch(fetchRequest)
            for entry in entries {
                context.delete(entry)
            }
            try context.save()
            print("Cleaned up \(entries.count) old time entries")
        } catch {
            print("Error cleaning up time entries: \(error)")
        }
    }

    private func cleanupExpiredReminders() {
        let context = PersistenceController.shared.container.viewContext

        // Delete non-repeating reminders older than 7 days
        let sevenDaysAgo = Calendar.current.date(byAdding: .day, value: -7, to: Date())!

        let fetchRequest = Reminder.fetchRequest()
        fetchRequest.predicate = NSPredicate(
            format: "isRepeating == NO AND date < %@",
            sevenDaysAgo as NSDate
        )

        do {
            let reminders = try context.fetch(fetchRequest)
            for reminder in reminders {
                context.delete(reminder)
            }
            try context.save()
            print("Cleaned up \(reminders.count) expired reminders")
        } catch {
            print("Error cleaning up reminders: \(error)")
        }
    }
}
