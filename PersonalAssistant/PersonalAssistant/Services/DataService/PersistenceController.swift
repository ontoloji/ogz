//
//  PersistenceController.swift
//  PersonalAssistant
//
//  Core Data persistence controller
//

import CoreData
import CloudKit

class PersistenceController: ObservableObject {
    static let shared = PersistenceController()

    // Preview instance for SwiftUI previews
    static var preview: PersistenceController = {
        let controller = PersistenceController(inMemory: true)
        let viewContext = controller.container.viewContext

        // Create sample data for previews
        for i in 0..<10 {
            let note = Note(context: viewContext)
            note.id = UUID()
            note.title = "Sample Note \(i)"
            note.content = "This is a sample note content"
            note.createdAt = Date().addingTimeInterval(Double(-i * 86400))
            note.modifiedAt = Date()
            note.isPinned = i % 3 == 0
            note.priority = Int16(i % 3)
        }

        do {
            try viewContext.save()
        } catch {
            fatalError("Preview data creation failed: \(error.localizedDescription)")
        }

        return controller
    }()

    let container: NSPersistentCloudKitContainer

    init(inMemory: Bool = false) {
        container = NSPersistentCloudKitContainer(name: "PersonalAssistant")

        if inMemory {
            container.persistentStoreDescriptions.first?.url = URL(fileURLWithPath: "/dev/null")
        } else {
            // Configure CloudKit container
            guard let description = container.persistentStoreDescriptions.first else {
                fatalError("Failed to retrieve persistent store description")
            }

            // Enable persistent history tracking
            description.setOption(true as NSNumber, forKey: NSPersistentHistoryTrackingKey)
            description.setOption(true as NSNumber, forKey: NSPersistentStoreRemoteChangeNotificationPostOptionKey)

            // Enable CloudKit sync
            description.cloudKitContainerOptions = NSPersistentCloudKitContainerOptions(
                containerIdentifier: "iCloud.com.personalassistant.app"
            )
        }

        container.loadPersistentStores { storeDescription, error in
            if let error = error as NSError? {
                // Handle the error appropriately in production
                fatalError("Unresolved error \(error), \(error.userInfo)")
            }
        }

        // Configure view context
        container.viewContext.automaticallyMergesChangesFromParent = true
        container.viewContext.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy

        // Setup notifications for iCloud changes
        setupCloudKitNotifications()
    }

    // MARK: - Save Context

    func save() {
        let context = container.viewContext

        if context.hasChanges {
            do {
                try context.save()
            } catch {
                let nsError = error as NSError
                print("Error saving context: \(nsError), \(nsError.userInfo)")
            }
        }
    }

    // MARK: - Background Context

    func performBackgroundTask(_ block: @escaping (NSManagedObjectContext) -> Void) {
        container.performBackgroundTask(block)
    }

    // MARK: - CloudKit Notifications

    private func setupCloudKitNotifications() {
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(handleCloudKitRemoteChange(_:)),
            name: .NSPersistentStoreRemoteChange,
            object: container.persistentStoreCoordinator
        )
    }

    @objc private func handleCloudKitRemoteChange(_ notification: Notification) {
        print("Remote change detected in CloudKit")
        // Handle sync completion
        NotificationCenter.default.post(name: .syncCompleted, object: nil)
    }

    // MARK: - Batch Operations

    func batchDelete<T: NSManagedObject>(fetchRequest: NSFetchRequest<T>) async throws {
        let deleteRequest = NSBatchDeleteRequest(fetchRequest: fetchRequest as! NSFetchRequest<NSFetchRequestResult>)
        deleteRequest.resultType = .resultTypeObjectIDs

        let context = container.viewContext
        let result = try context.execute(deleteRequest) as? NSBatchDeleteResult
        let objectIDArray = result?.result as? [NSManagedObjectID] ?? []
        let changes = [NSDeletedObjectsKey: objectIDArray]

        NSManagedObjectContext.mergeChanges(fromRemoteContextSave: changes, into: [context])
    }

    // MARK: - Fetch Operations

    func fetch<T: NSManagedObject>(_ request: NSFetchRequest<T>) -> [T] {
        do {
            return try container.viewContext.fetch(request)
        } catch {
            print("Error fetching: \(error)")
            return []
        }
    }

    func count<T: NSManagedObject>(_ request: NSFetchRequest<T>) -> Int {
        do {
            return try container.viewContext.count(for: request)
        } catch {
            print("Error counting: \(error)")
            return 0
        }
    }

    deinit {
        NotificationCenter.default.removeObserver(self)
    }
}
