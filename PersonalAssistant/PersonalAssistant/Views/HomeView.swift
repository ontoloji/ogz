//
//  HomeView.swift
//  PersonalAssistant
//
//  Main home dashboard view
//

import SwiftUI
import CoreData

struct HomeView: View {
    @Environment(\.managedObjectContext) private var viewContext
    @EnvironmentObject var calendarManager: CalendarManager

    @FetchRequest(
        fetchRequest: Note.pinnedNotesFetchRequest(),
        animation: .default
    )
    private var pinnedNotes: FetchedResults<Note>

    @FetchRequest(
        fetchRequest: Task.todayTasks(),
        animation: .default
    )
    private var todayTasks: FetchedResults<Task>

    @FetchRequest(
        fetchRequest: Task.overdueTasks(),
        animation: .default
    )
    private var overdueTasks: FetchedResults<Task>

    @State private var greeting = ""

    var body: some View {
        NavigationView {
            ScrollView {
                VStack(alignment: .leading, spacing: 20) {
                    // Greeting Header
                    VStack(alignment: .leading, spacing: 5) {
                        Text(greeting)
                            .font(.title2)
                            .fontWeight(.bold)

                        Text("Bugün neler yapacaksın?")
                            .font(.subheadline)
                            .foregroundColor(.secondary)
                    }
                    .padding(.horizontal)
                    .padding(.top)

                    // Quick Stats
                    QuickStatsView(
                        todayTasksCount: todayTasks.count,
                        overdueTasksCount: overdueTasks.count,
                        pinnedNotesCount: pinnedNotes.count,
                        upcomingEventsCount: calendarManager.todayEvents.count
                    )
                    .padding(.horizontal)

                    // Today's Events
                    if !calendarManager.todayEvents.isEmpty {
                        VStack(alignment: .leading, spacing: 10) {
                            SectionHeader(title: "Bugünkü Etkinlikler", icon: "calendar")
                                .padding(.horizontal)

                            ScrollView(.horizontal, showsIndicators: false) {
                                HStack(spacing: 15) {
                                    ForEach(calendarManager.todayEvents, id: \.eventIdentifier) { event in
                                        EventCardView(event: event)
                                    }
                                }
                                .padding(.horizontal)
                            }
                        }
                    }

                    // Overdue Tasks
                    if !overdueTasks.isEmpty {
                        VStack(alignment: .leading, spacing: 10) {
                            SectionHeader(title: "Gecikmiş Görevler", icon: "exclamationmark.triangle.fill")
                                .padding(.horizontal)

                            ForEach(overdueTasks.prefix(3)) { task in
                                TaskRowView(task: task)
                                    .padding(.horizontal)
                            }

                            if overdueTasks.count > 3 {
                                NavigationLink(destination: TasksView()) {
                                    Text("Tümünü Gör (\(overdueTasks.count - 3) daha)")
                                        .font(.footnote)
                                        .foregroundColor(.blue)
                                }
                                .padding(.horizontal)
                            }
                        }
                    }

                    // Today's Tasks
                    if !todayTasks.isEmpty {
                        VStack(alignment: .leading, spacing: 10) {
                            SectionHeader(title: "Bugünkü Görevler", icon: "checkmark.circle")
                                .padding(.horizontal)

                            ForEach(todayTasks.prefix(5)) { task in
                                TaskRowView(task: task)
                                    .padding(.horizontal)
                            }

                            if todayTasks.count > 5 {
                                NavigationLink(destination: TasksView()) {
                                    Text("Tümünü Gör (\(todayTasks.count - 5) daha)")
                                        .font(.footnote)
                                        .foregroundColor(.blue)
                                }
                                .padding(.horizontal)
                            }
                        }
                    }

                    // Pinned Notes
                    if !pinnedNotes.isEmpty {
                        VStack(alignment: .leading, spacing: 10) {
                            SectionHeader(title: "Sabitlenmiş Notlar", icon: "pin.fill")
                                .padding(.horizontal)

                            ForEach(pinnedNotes.prefix(3)) { note in
                                NoteCardView(note: note)
                                    .padding(.horizontal)
                            }

                            if pinnedNotes.count > 3 {
                                NavigationLink(destination: NotesListView()) {
                                    Text("Tümünü Gör (\(pinnedNotes.count - 3) daha)")
                                        .font(.footnote)
                                        .foregroundColor(.blue)
                                }
                                .padding(.horizontal)
                            }
                        }
                    }

                    // Empty state
                    if todayTasks.isEmpty && pinnedNotes.isEmpty && calendarManager.todayEvents.isEmpty {
                        EmptyHomeView()
                            .padding()
                    }
                }
                .padding(.bottom)
            }
            .navigationTitle("Ana Sayfa")
            .navigationBarTitleDisplayMode(.inline)
            .refreshable {
                await refreshData()
            }
            .onAppear {
                updateGreeting()
                calendarManager.loadTodayEvents()
            }
        }
    }

    private func updateGreeting() {
        let hour = Calendar.current.component(.hour, from: Date())
        switch hour {
        case 0..<12:
            greeting = "Günaydın ☀️"
        case 12..<18:
            greeting = "İyi günler ☀️"
        case 18..<22:
            greeting = "İyi akşamlar 🌙"
        default:
            greeting = "İyi geceler 🌙"
        }
    }

    private func refreshData() async {
        calendarManager.loadTodayEvents()
        calendarManager.loadUpcomingEvents()
    }
}

// MARK: - Supporting Views

struct QuickStatsView: View {
    let todayTasksCount: Int
    let overdueTasksCount: Int
    let pinnedNotesCount: Int
    let upcomingEventsCount: Int

    var body: some View {
        HStack(spacing: 12) {
            StatCard(value: todayTasksCount, label: "Bugün", icon: "checkmark.circle.fill", color: .blue)
            StatCard(value: overdueTasksCount, label: "Gecikmiş", icon: "exclamationmark.triangle.fill", color: .red)
            StatCard(value: upcomingEventsCount, label: "Etkinlik", icon: "calendar", color: .green)
        }
    }
}

struct StatCard: View {
    let value: Int
    let label: String
    let icon: String
    let color: Color

    var body: some View {
        VStack(spacing: 8) {
            HStack(spacing: 4) {
                Image(systemName: icon)
                    .font(.caption)
                Text("\(value)")
                    .font(.title2)
                    .fontWeight(.bold)
            }
            .foregroundColor(color)

            Text(label)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding()
        .background(Color.cardBackground)
        .cornerRadius(15)
    }
}

struct SectionHeader: View {
    let title: String
    let icon: String

    var body: some View {
        HStack {
            Image(systemName: icon)
                .foregroundColor(.blue)
            Text(title)
                .font(.headline)
                .fontWeight(.semibold)
        }
    }
}

struct EmptyHomeView: View {
    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: "checkmark.circle")
                .font(.system(size: 60))
                .foregroundColor(.green)

            Text("Harika! Bugün hiç görevin yok.")
                .font(.title3)
                .fontWeight(.semibold)
                .multilineTextAlignment(.center)

            Text("Yeni bir not ekleyebilir veya yaklaşan görevlerini planla yabilirsin.")
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .padding(40)
    }
}
