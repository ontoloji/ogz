//
//  CloudKitManager.swift
//  PersonalAssistant
//
//  Manages CloudKit synchronization
//

import Foundation
import CloudKit
import CoreData

@MainActor
class CloudKitManager: ObservableObject {
    static let shared = CloudKitManager()

    @Published var isSyncing = false
    @Published var lastSyncDate: Date?
    @Published var syncError: Error?

    private let container: CKContainer
    private let privateDatabase: CKDatabase

    var isCloudKitAvailable: Bool {
        FileManager.default.ubiquityIdentityToken != nil
    }

    init() {
        container = CKContainer(identifier: "iCloud.com.personalassistant.app")
        privateDatabase = container.privateCloudDatabase

        lastSyncDate = UserDefaults.standard.object(forKey: "lastSyncDate") as? Date

        setupSubscriptions()
    }

    // MARK: - Sync

    func syncWithCloud() async {
        guard isCloudKitAvailable else {
            print("iCloud not available")
            return
        }

        guard !isSyncing else {
            print("Sync already in progress")
            return
        }

        await MainActor.run {
            isSyncing = true
            syncError = nil
        }

        do {
            // CloudKit sync is handled automatically by NSPersistentCloudKitContainer
            // This method is for manual sync triggers and custom logic

            // Fetch remote changes
            try await fetchRemoteChanges()

            // Update last sync date
            await MainActor.run {
                lastSyncDate = Date()
                UserDefaults.standard.set(lastSyncDate, forKey: "lastSyncDate")
                isSyncing = false
            }

            // Notify completion
            NotificationCenter.default.post(name: .syncCompleted, object: nil)

        } catch {
            print("Sync error: \(error)")
            await MainActor.run {
                syncError = error
                isSyncing = false
            }
        }
    }

    private func fetchRemoteChanges() async throws {
        // NSPersistentCloudKitContainer handles this automatically
        // Additional custom sync logic can be added here
    }

    // MARK: - CloudKit Subscriptions

    private func setupSubscriptions() {
        Task {
            await createDatabaseSubscription()
        }
    }

    private func createDatabaseSubscription() async {
        let subscriptionID = "database-changes"

        // Check if subscription already exists
        do {
            _ = try await privateDatabase.subscription(for: subscriptionID)
            print("Subscription already exists")
            return
        } catch {
            // Subscription doesn't exist, create it
        }

        let subscription = CKDatabaseSubscription(subscriptionID: subscriptionID)

        let notificationInfo = CKSubscription.NotificationInfo()
        notificationInfo.shouldSendContentAvailable = true

        subscription.notificationInfo = notificationInfo

        do {
            _ = try await privateDatabase.save(subscription)
            print("Successfully created database subscription")
        } catch {
            print("Error creating subscription: \(error)")
        }
    }

    // MARK: - Account Status

    func checkAccountStatus() async -> CKAccountStatus {
        do {
            let status = try await container.accountStatus()
            return status
        } catch {
            print("Error checking account status: \(error)")
            return .couldNotDetermine
        }
    }

    func isSignedInToiCloud() async -> Bool {
        let status = await checkAccountStatus()
        return status == .available
    }

    // MARK: - Custom CloudKit Operations (if needed)

    func saveRecord(_ record: CKRecord) async throws {
        _ = try await privateDatabase.save(record)
    }

    func fetchRecord(withID recordID: CKRecord.ID) async throws -> CKRecord {
        return try await privateDatabase.record(for: recordID)
    }

    func deleteRecord(withID recordID: CKRecord.ID) async throws {
        _ = try await privateDatabase.deleteRecord(withID: recordID)
    }

    // MARK: - Sync Status

    var syncStatusText: String {
        if isSyncing {
            return "Senkronize ediliyor..."
        } else if let lastSync = lastSyncDate {
            let formatter = RelativeDateTimeFormatter()
            formatter.unitsStyle = .full
            return "Son senkronizasyon: \(formatter.localizedString(for: lastSync, relativeTo: Date()))"
        } else {
            return "Henüz senkronize edilmedi"
        }
    }

    // MARK: - Error Handling

    func handleSyncError(_ error: Error) {
        if let ckError = error as? CKError {
            switch ckError.code {
            case .networkUnavailable, .networkFailure:
                print("Network error: \(ckError.localizedDescription)")
            case .notAuthenticated:
                print("Not signed in to iCloud")
            case .quotaExceeded:
                print("iCloud quota exceeded")
            case .zoneBusy, .serviceUnavailable:
                print("Service temporarily unavailable, will retry")
            default:
                print("CloudKit error: \(ckError.localizedDescription)")
            }
        }
    }
}
