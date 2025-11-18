//
//  Project+Extensions.swift
//  PersonalAssistant
//
//  Project entity extensions
//

import Foundation
import CoreData
import SwiftUI

extension Project {
    var wrappedName: String {
        name ?? ""
    }

    var wrappedDescription: String {
        projectDescription ?? ""
    }

    var projectColor: Color {
        Color(hex: colorHex ?? "#007AFF") ?? .blue
    }

    var tasksArray: [Task] {
        let set = tasks as? Set<Task> ?? []
        return set.sorted { $0.sortOrder < $1.sortOrder }
    }

    var completedTasksCount: Int {
        tasksArray.filter { $0.isCompleted }.count
    }

    var totalTasksCount: Int {
        tasksArray.count
    }

    var calculatedProgress: Float {
        guard totalTasksCount > 0 else { return 0 }
        return Float(completedTasksCount) / Float(totalTasksCount)
    }

    var isOverdue: Bool {
        guard let deadline = deadline, !isArchived else { return false }
        return deadline < Date() && calculatedProgress < 1.0
    }

    var daysUntilDeadline: Int? {
        guard let deadline = deadline else { return nil }
        let days = Calendar.current.dateComponents([.day], from: Date(), to: deadline).day
        return days
    }

    // Create project
    static func create(
        in context: NSManagedObjectContext,
        name: String,
        description: String = "",
        colorHex: String = "#007AFF",
        deadline: Date? = nil
    ) -> Project {
        let project = Project(context: context)
        project.id = UUID()
        project.name = name
        project.projectDescription = description
        project.colorHex = colorHex
        project.createdAt = Date()
        project.deadline = deadline
        project.progress = 0
        project.isArchived = false
        return project
    }

    // Update progress
    func updateProgress() {
        progress = calculatedProgress
    }

    // Archive project
    func archive() {
        isArchived = true
    }

    // Fetch requests
    static func fetchRequest() -> NSFetchRequest<Project> {
        return NSFetchRequest<Project>(entityName: "Project")
    }

    static func activeProjects() -> NSFetchRequest<Project> {
        let request = fetchRequest()
        request.sortDescriptors = [NSSortDescriptor(keyPath: \Project.createdAt, ascending: false)]
        request.predicate = NSPredicate(format: "isArchived == NO")
        return request
    }

    static func archivedProjects() -> NSFetchRequest<Project> {
        let request = fetchRequest()
        request.sortDescriptors = [NSSortDescriptor(keyPath: \Project.createdAt, ascending: false)]
        request.predicate = NSPredicate(format: "isArchived == YES")
        return request
    }
}
