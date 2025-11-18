//
//  Task+Extensions.swift
//  PersonalAssistant
//
//  Task entity extensions
//

import Foundation
import CoreData
import SwiftUI

extension Task {
    var wrappedTitle: String {
        title ?? ""
    }

    var wrappedDescription: String {
        taskDescription ?? ""
    }

    var priorityLevel: Note.Priority {
        Note.Priority(rawValue: Int(priority)) ?? .normal
    }

    var tagsArray: [Tag] {
        let set = tags as? Set<Tag> ?? []
        return set.sorted { $0.name ?? "" < $1.name ?? "" }
    }

    var subtasksArray: [Task] {
        let set = subtasks as? Set<Task> ?? []
        return set.sorted { $0.sortOrder < $1.sortOrder }
    }

    var timeEntriesArray: [TimeEntry] {
        let set = timeEntries as? Set<TimeEntry> ?? []
        return set.sorted { $0.startTime ?? Date() > $1.startTime ?? Date() }
    }

    var completionPercentage: Double {
        guard !subtasksArray.isEmpty else { return isCompleted ? 1.0 : 0.0 }
        let completed = subtasksArray.filter { $0.isCompleted }.count
        return Double(completed) / Double(subtasksArray.count)
    }

    var totalTimeSpent: Int {
        return timeEntriesArray.reduce(0) { $0 + Int($1.duration) }
    }

    var isOverdue: Bool {
        guard let dueDate = dueDate, !isCompleted else { return false }
        return dueDate < Date()
    }

    var isDueToday: Bool {
        guard let dueDate = dueDate else { return false }
        return Calendar.current.isDateInToday(dueDate)
    }

    var isDueTomorrow: Bool {
        guard let dueDate = dueDate else { return false }
        return Calendar.current.isDateInTomorrow(dueDate)
    }

    // Create task
    static func create(
        in context: NSManagedObjectContext,
        title: String,
        description: String = "",
        dueDate: Date? = nil,
        priority: Note.Priority = .normal,
        category: Category? = nil,
        project: Project? = nil
    ) -> Task {
        let task = Task(context: context)
        task.id = UUID()
        task.title = title
        task.taskDescription = description
        task.createdAt = Date()
        task.modifiedAt = Date()
        task.dueDate = dueDate
        task.priority = Int16(priority.rawValue)
        task.isCompleted = false
        task.category = category
        task.project = project
        return task
    }

    // Toggle completion
    func toggleCompletion() {
        isCompleted.toggle()
        if isCompleted {
            completedAt = Date()
        } else {
            completedAt = nil
        }
        modifiedAt = Date()
    }

    // Add subtask
    func addSubtask(title: String, in context: NSManagedObjectContext) -> Task {
        let subtask = Task.create(in: context, title: title)
        subtask.parentTask = self
        subtask.sortOrder = Int16(subtasksArray.count)
        return subtask
    }

    // Start time tracking
    func startTimeTracking(in context: NSManagedObjectContext) -> TimeEntry {
        let entry = TimeEntry(context: context)
        entry.id = UUID()
        entry.startTime = Date()
        entry.task = self
        return entry
    }

    // Fetch requests
    static func fetchRequest() -> NSFetchRequest<Task> {
        return NSFetchRequest<Task>(entityName: "Task")
    }

    static func allTasksFetchRequest() -> NSFetchRequest<Task> {
        let request = fetchRequest()
        request.sortDescriptors = [
            NSSortDescriptor(keyPath: \Task.isCompleted, ascending: true),
            NSSortDescriptor(keyPath: \Task.priority, ascending: false),
            NSSortDescriptor(keyPath: \Task.dueDate, ascending: true)
        ]
        request.predicate = NSPredicate(format: "parentTask == nil")
        return request
    }

    static func incompleteTasks() -> NSFetchRequest<Task> {
        let request = fetchRequest()
        request.sortDescriptors = [
            NSSortDescriptor(keyPath: \Task.priority, ascending: false),
            NSSortDescriptor(keyPath: \Task.dueDate, ascending: true)
        ]
        request.predicate = NSPredicate(format: "isCompleted == NO AND parentTask == nil")
        return request
    }

    static func completedTasks() -> NSFetchRequest<Task> {
        let request = fetchRequest()
        request.sortDescriptors = [NSSortDescriptor(keyPath: \Task.completedAt, ascending: false)]
        request.predicate = NSPredicate(format: "isCompleted == YES AND parentTask == nil")
        return request
    }

    static func todayTasks() -> NSFetchRequest<Task> {
        let calendar = Calendar.current
        let startOfDay = calendar.startOfDay(for: Date())
        let endOfDay = calendar.date(byAdding: .day, value: 1, to: startOfDay)!

        let request = fetchRequest()
        request.sortDescriptors = [
            NSSortDescriptor(keyPath: \Task.priority, ascending: false),
            NSSortDescriptor(keyPath: \Task.dueDate, ascending: true)
        ]
        request.predicate = NSPredicate(
            format: "dueDate >= %@ AND dueDate < %@ AND isCompleted == NO AND parentTask == nil",
            startOfDay as NSDate, endOfDay as NSDate
        )
        return request
    }

    static func overdueTasks() -> NSFetchRequest<Task> {
        let request = fetchRequest()
        request.sortDescriptors = [NSSortDescriptor(keyPath: \Task.dueDate, ascending: true)]
        request.predicate = NSPredicate(
            format: "dueDate < %@ AND isCompleted == NO AND parentTask == nil",
            Date() as NSDate
        )
        return request
    }

    static func tasksByProject(_ project: Project) -> NSFetchRequest<Task> {
        let request = fetchRequest()
        request.sortDescriptors = [
            NSSortDescriptor(keyPath: \Task.isCompleted, ascending: true),
            NSSortDescriptor(keyPath: \Task.sortOrder, ascending: true)
        ]
        request.predicate = NSPredicate(format: "project == %@", project)
        return request
    }
}
