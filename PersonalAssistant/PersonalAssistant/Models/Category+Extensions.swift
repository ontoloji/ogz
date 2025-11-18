//
//  Category+Extensions.swift
//  PersonalAssistant
//
//  Category entity extensions
//

import Foundation
import CoreData
import SwiftUI

extension Category {
    var wrappedName: String {
        name ?? "Uncategorized"
    }

    var wrappedColorHex: String {
        colorHex ?? "#007AFF"
    }

    var wrappedIconName: String {
        iconName ?? "folder"
    }

    var categoryColor: Color {
        Color(hex: wrappedColorHex) ?? .blue
    }

    var notesArray: [Note] {
        let set = notes as? Set<Note> ?? []
        return set.sorted { $0.modifiedAt ?? Date() > $1.modifiedAt ?? Date() }
    }

    var tasksArray: [Task] {
        let set = tasks as? Set<Task> ?? []
        return set.sorted { $0.createdAt ?? Date() > $1.createdAt ?? Date() }
    }

    var notesCount: Int {
        notesArray.filter { !$0.isArchived }.count
    }

    var tasksCount: Int {
        tasksArray.filter { !$0.isCompleted }.count
    }

    // Predefined categories
    static let defaultCategories = [
        ("İş", "#FF6B6B", "briefcase.fill"),
        ("Kişisel", "#4ECDC4", "person.fill"),
        ("Alışveriş", "#95E1D3", "cart.fill"),
        ("Sağlık", "#F38181", "heart.fill"),
        ("Eğitim", "#AA96DA", "book.fill"),
        ("Finans", "#FCBAD3", "dollarsign.circle.fill"),
        ("Seyahat", "#FFFFD2", "airplane"),
        ("Hobi", "#A8D8EA", "paintpalette.fill")
    ]

    // Create category
    static func create(
        in context: NSManagedObjectContext,
        name: String,
        colorHex: String = "#007AFF",
        iconName: String = "folder"
    ) -> Category {
        let category = Category(context: context)
        category.id = UUID()
        category.name = name
        category.colorHex = colorHex
        category.iconName = iconName
        category.createdAt = Date()
        category.sortOrder = 0
        return category
    }

    // Initialize default categories
    static func createDefaultCategories(in context: NSManagedObjectContext) {
        for (index, (name, color, icon)) in defaultCategories.enumerated() {
            let category = create(in: context, name: name, colorHex: color, iconName: icon)
            category.sortOrder = Int16(index)
        }

        do {
            try context.save()
        } catch {
            print("Error creating default categories: \(error)")
        }
    }

    // Fetch requests
    static func fetchRequest() -> NSFetchRequest<Category> {
        return NSFetchRequest<Category>(entityName: "Category")
    }

    static func allCategoriesFetchRequest() -> NSFetchRequest<Category> {
        let request = fetchRequest()
        request.sortDescriptors = [NSSortDescriptor(keyPath: \Category.sortOrder, ascending: true)]
        return request
    }
}
