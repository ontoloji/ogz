//
//  Note+Extensions.swift
//  PersonalAssistant
//
//  Note entity extensions
//

import Foundation
import CoreData
import SwiftUI

extension Note {
    // Computed properties for easier access
    var wrappedTitle: String {
        title ?? ""
    }

    var wrappedContent: String {
        content ?? ""
    }

    var categoryColor: Color {
        if let colorHex = colorHex {
            return Color(hex: colorHex) ?? .blue
        }
        return category?.categoryColor ?? .blue
    }

    var priorityLevel: Priority {
        Priority(rawValue: Int(priority)) ?? .normal
    }

    var tagsArray: [Tag] {
        let set = tags as? Set<Tag> ?? []
        return set.sorted { $0.name ?? "" < $1.name ?? "" }
    }

    var remindersArray: [Reminder] {
        let set = reminders as? Set<Reminder> ?? []
        return set.sorted { $0.date ?? Date() < $1.date ?? Date() }
    }

    var nextReminder: Reminder? {
        return remindersArray.first { ($0.date ?? Date()) > Date() && $0.isEnabled }
    }

    var imageURLsArray: [String] {
        return (imageURLs as? [String]) ?? []
    }

    // Priority enum
    enum Priority: Int, CaseIterable {
        case low = 0
        case normal = 1
        case high = 2

        var displayName: String {
            switch self {
            case .low: return "Düşük"
            case .normal: return "Normal"
            case .high: return "Yüksek"
            }
        }

        var color: Color {
            switch self {
            case .low: return .green
            case .normal: return .blue
            case .high: return .red
            }
        }

        var icon: String {
            switch self {
            case .low: return "arrow.down.circle"
            case .normal: return "circle"
            case .high: return "exclamationmark.circle"
            }
        }
    }

    // Create new note
    static func create(
        in context: NSManagedObjectContext,
        title: String,
        content: String = "",
        category: Category? = nil,
        priority: Priority = .normal
    ) -> Note {
        let note = Note(context: context)
        note.id = UUID()
        note.title = title
        note.content = content
        note.createdAt = Date()
        note.modifiedAt = Date()
        note.category = category
        note.priority = Int16(priority.rawValue)
        note.isPinned = false
        note.isArchived = false
        note.isLocked = false
        note.hasReminder = false
        return note
    }

    // Update note
    func update(title: String? = nil, content: String? = nil) {
        if let title = title {
            self.title = title
        }
        if let content = content {
            self.content = content
        }
        self.modifiedAt = Date()
    }

    // Toggle pin
    func togglePin() {
        isPinned.toggle()
        modifiedAt = Date()
    }

    // Archive note
    func archive() {
        isArchived = true
        modifiedAt = Date()
    }

    // Unarchive note
    func unarchive() {
        isArchived = false
        modifiedAt = Date()
    }

    // Add reminder
    func addReminder(date: Date, in context: NSManagedObjectContext) {
        let reminder = Reminder(context: context)
        reminder.id = UUID()
        reminder.date = date
        reminder.isEnabled = true
        reminder.note = self
        hasReminder = true
        reminderDate = date
        modifiedAt = Date()
    }

    // Fetch request helpers
    static func fetchRequest() -> NSFetchRequest<Note> {
        return NSFetchRequest<Note>(entityName: "Note")
    }

    static func allNotesFetchRequest() -> NSFetchRequest<Note> {
        let request = fetchRequest()
        request.sortDescriptors = [
            NSSortDescriptor(keyPath: \Note.isPinned, ascending: false),
            NSSortDescriptor(keyPath: \Note.modifiedAt, ascending: false)
        ]
        request.predicate = NSPredicate(format: "isArchived == NO")
        return request
    }

    static func pinnedNotesFetchRequest() -> NSFetchRequest<Note> {
        let request = fetchRequest()
        request.sortDescriptors = [NSSortDescriptor(keyPath: \Note.modifiedAt, ascending: false)]
        request.predicate = NSPredicate(format: "isPinned == YES AND isArchived == NO")
        return request
    }

    static func archivedNotesFetchRequest() -> NSFetchRequest<Note> {
        let request = fetchRequest()
        request.sortDescriptor = [NSSortDescriptor(keyPath: \Note.modifiedAt, ascending: false)]
        request.predicate = NSPredicate(format: "isArchived == YES")
        return request
    }

    static func notesByCategory(_ category: Category) -> NSFetchRequest<Note> {
        let request = fetchRequest()
        request.sortDescriptors = [
            NSSortDescriptor(keyPath: \Note.isPinned, ascending: false),
            NSSortDescriptor(keyPath: \Note.modifiedAt, ascending: false)
        ]
        request.predicate = NSPredicate(format: "category == %@ AND isArchived == NO", category)
        return request
    }

    static func searchNotes(query: String) -> NSFetchRequest<Note> {
        let request = fetchRequest()
        request.sortDescriptors = [NSSortDescriptor(keyPath: \Note.modifiedAt, ascending: false)]
        request.predicate = NSPredicate(
            format: "(title CONTAINS[cd] %@ OR content CONTAINS[cd] %@) AND isArchived == NO",
            query, query
        )
        return request
    }
}

// Color extension for hex support
extension Color {
    init?(hex: String) {
        var hexSanitized = hex.trimmingCharacters(in: .whitespacesAndNewlines)
        hexSanitized = hexSanitized.replacingOccurrences(of: "#", with: "")

        var rgb: UInt64 = 0
        guard Scanner(string: hexSanitized).scanHexInt64(&rgb) else { return nil }

        let r = Double((rgb & 0xFF0000) >> 16) / 255.0
        let g = Double((rgb & 0x00FF00) >> 8) / 255.0
        let b = Double(rgb & 0x0000FF) / 255.0

        self.init(red: r, green: g, blue: b)
    }

    func toHex() -> String? {
        guard let components = UIColor(self).cgColor.components else { return nil }
        let r = Float(components[0])
        let g = Float(components[1])
        let b = Float(components[2])
        return String(format: "#%02lX%02lX%02lX",
                     lroundf(r * 255),
                     lroundf(g * 255),
                     lroundf(b * 255))
    }
}
