//
//  TasksView.swift
//  PersonalAssistant
//
//  Tasks management view
//

import SwiftUI

struct TasksView: View {
    @Environment(\.managedObjectContext) private var viewContext

    @FetchRequest(
        fetchRequest: Task.incompleteTasks(),
        animation: .default
    )
    private var tasks: FetchedResults<Task>

    @State private var showingAddTask = false
    @State private var selectedFilter: TaskFilter = .all
    @State private var showPomodoroTimer = false

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Filter Segment
                Picker("Filter", selection: $selectedFilter) {
                    ForEach(TaskFilter.allCases, id: \.self) { filter in
                        Text(filter.displayName).tag(filter)
                    }
                }
                .pickerStyle(.segmented)
                .padding()

                // Task List
                if filteredTasks.isEmpty {
                    EmptyTasksView()
                } else {
                    List {
                        ForEach(filteredTasks) { task in
                            TaskRowView(task: task)
                                .swipeActions(edge: .trailing) {
                                    Button(role: .destructive) {
                                        deleteTask(task)
                                    } label: {
                                        Label("Sil", systemImage: "trash")
                                    }
                                }
                                .listRowSeparator(.hidden)
                                .listRowBackground(Color.clear)
                        }
                    }
                    .listStyle(.plain)
                }
            }
            .navigationTitle("Görevler")
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button(action: { showPomodoroTimer = true }) {
                        Image(systemName: "timer")
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showingAddTask = true }) {
                        Image(systemName: "plus.circle.fill")
                    }
                }
            }
            .sheet(isPresented: $showingAddTask) {
                AddTaskView()
            }
            .sheet(isPresented: $showPomodoroTimer) {
                PomodoroTimerView()
            }
        }
    }

    private var filteredTasks: [Task] {
        Array(tasks).filter { task in
            switch selectedFilter {
            case .all:
                return true
            case .today:
                return task.isDueToday
            case .upcoming:
                return task.dueDate ?? Date.distantFuture > Date()
            case .highPriority:
                return task.priority >= 2
            }
        }
    }

    private func deleteTask(_ task: Task) {
        viewContext.delete(task)
        try? viewContext.save()
        HapticManager.shared.success()
    }

    enum TaskFilter: CaseIterable {
        case all, today, upcoming, highPriority

        var displayName: String {
            switch self {
            case .all: return "Tümü"
            case .today: return "Bugün"
            case .upcoming: return "Yaklaşan"
            case .highPriority: return "Öncelikli"
            }
        }
    }
}

struct AddTaskView: View {
    @Environment(\.managedObjectContext) private var viewContext
    @Environment(\.dismiss) private var dismiss

    @State private var title = ""
    @State private var description = ""
    @State private var dueDate = Date()
    @State private var hasDueDate = false
    @State private var priority: Note.Priority = .normal

    var body: some View {
        NavigationView {
            Form {
                TextField("Görev başlığı", text: $title)

                Section("Açıklama") {
                    TextEditor(text: $description)
                        .frame(minHeight: 80)
                }

                Section("Son Tarih") {
                    Toggle("Son tarih ekle", isOn: $hasDueDate)
                    if hasDueDate {
                        DatePicker("Tarih", selection: $dueDate, in: Date()...)
                    }
                }

                Section("Öncelik") {
                    Picker("Öncelik", selection: $priority) {
                        ForEach(Note.Priority.allCases, id: \.self) { priority in
                            Text(priority.displayName).tag(priority)
                        }
                    }
                    .pickerStyle(.segmented)
                }
            }
            .navigationTitle("Yeni Görev")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("İptal") { dismiss() }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button("Kaydet") {
                        saveTask()
                    }
                    .disabled(title.isEmpty)
                }
            }
        }
    }

    private func saveTask() {
        _ = Task.create(
            in: viewContext,
            title: title,
            description: description,
            dueDate: hasDueDate ? dueDate : nil,
            priority: priority
        )

        try? viewContext.save()
        HapticManager.shared.success()
        dismiss()
    }
}

struct EmptyTasksView: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "checkmark.circle")
                .font(.system(size: 60))
                .foregroundColor(.green)

            Text("Harika! Hiç görevin yok")
                .font(.title3)
                .fontWeight(.semibold)

            Text("Yeni bir görev eklemek için + butonuna dokun")
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .padding(40)
    }
}
