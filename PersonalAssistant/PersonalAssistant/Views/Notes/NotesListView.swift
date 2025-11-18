//
//  NotesListView.swift
//  PersonalAssistant
//
//  Main notes list view
//

import SwiftUI
import CoreData

struct NotesListView: View {
    @Environment(\.managedObjectContext) private var viewContext

    @FetchRequest(
        fetchRequest: Note.allNotesFetchRequest(),
        animation: .default
    )
    private var notes: FetchedResults<Note>

    @FetchRequest(
        fetchRequest: Category.allCategoriesFetchRequest(),
        animation: .default
    )
    private var categories: FetchedResults<Category>

    @State private var searchText = ""
    @State private var showingAddNote = false
    @State private var selectedCategory: Category?
    @State private var showArchivedNotes = false
    @State private var sortOption: SortOption = .modifiedDate

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Search bar
                SearchBar(text: $searchText)
                    .padding()

                // Category filter
                if !categories.isEmpty {
                    ScrollView(.horizontal, showsIndicators: false) {
                        HStack(spacing: 10) {
                            // All notes chip
                            FilterChip(
                                title: "Tümü",
                                icon: "square.grid.2x2",
                                isSelected: selectedCategory == nil,
                                action: { selectedCategory = nil }
                            )

                            // Category chips
                            ForEach(categories) { category in
                                FilterChip(
                                    title: category.wrappedName,
                                    icon: category.wrappedIconName,
                                    color: category.categoryColor,
                                    isSelected: selectedCategory?.id == category.id,
                                    action: { selectedCategory = category }
                                )
                            }
                        }
                        .padding(.horizontal)
                    }
                    .padding(.bottom)
                }

                // Notes list
                if filteredNotes.isEmpty {
                    EmptyNotesView(searchText: searchText)
                } else {
                    List {
                        ForEach(filteredNotes) { note in
                            NoteCardView(note: note)
                                .swipeActions(edge: .trailing, allowsFullSwipe: true) {
                                    Button(role: .destructive) {
                                        deleteNote(note)
                                    } label: {
                                        Label("Sil", systemImage: "trash")
                                    }

                                    Button {
                                        archiveNote(note)
                                    } label: {
                                        Label("Arşivle", systemImage: "archivebox")
                                    }
                                    .tint(.orange)
                                }
                                .swipeActions(edge: .leading) {
                                    Button {
                                        togglePin(note)
                                    } label: {
                                        Label(
                                            note.isPinned ? "Sabitlemeyi Kaldır" : "Sabitle",
                                            systemImage: note.isPinned ? "pin.slash" : "pin.fill"
                                        )
                                    }
                                    .tint(.yellow)
                                }
                                .listRowSeparator(.hidden)
                                .listRowBackground(Color.clear)
                                .listRowInsets(EdgeInsets(top: 4, leading: 16, bottom: 4, trailing: 16))
                        }
                    }
                    .listStyle(.plain)
                    .refreshable {
                        // Refresh data if needed
                    }
                }
            }
            .navigationTitle("Notlar")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Menu {
                        Picker("Sırala", selection: $sortOption) {
                            ForEach(SortOption.allCases, id: \.self) { option in
                                Label(option.displayName, systemImage: option.icon)
                                    .tag(option)
                            }
                        }

                        Divider()

                        Button(action: { showArchivedNotes.toggle() }) {
                            Label("Arşivlenmiş Notlar", systemImage: "archivebox")
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                    }
                }

                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showingAddNote = true }) {
                        Image(systemName: "plus.circle.fill")
                            .font(.title3)
                    }
                }
            }
            .sheet(isPresented: $showingAddNote) {
                AddNoteView()
            }
            .sheet(isPresented: $showArchivedNotes) {
                ArchivedNotesView()
            }
        }
    }

    // Filtered notes based on search and category
    private var filteredNotes: [Note] {
        var result = Array(notes)

        // Filter by category
        if let category = selectedCategory {
            result = result.filter { $0.category == category }
        }

        // Filter by search text
        if !searchText.isEmpty {
            result = result.filter { note in
                note.wrappedTitle.localizedCaseInsensitiveContains(searchText) ||
                note.wrappedContent.localizedCaseInsensitiveContains(searchText)
            }
        }

        // Sort
        switch sortOption {
        case .modifiedDate:
            result.sort { ($0.modifiedAt ?? Date()) > ($1.modifiedAt ?? Date()) }
        case .createdDate:
            result.sort { ($0.createdAt ?? Date()) > ($1.createdAt ?? Date()) }
        case .title:
            result.sort { $0.wrappedTitle < $1.wrappedTitle }
        case .priority:
            result.sort { $0.priority > $1.priority }
        }

        return result
    }

    // MARK: - Actions

    private func deleteNote(_ note: Note) {
        withAnimation {
            viewContext.delete(note)
            do {
                try viewContext.save()
                HapticManager.shared.success()
            } catch {
                print("Error deleting note: \(error)")
            }
        }
    }

    private func archiveNote(_ note: Note) {
        withAnimation {
            note.archive()
            do {
                try viewContext.save()
                HapticManager.shared.success()
            } catch {
                print("Error archiving note: \(error)")
            }
        }
    }

    private func togglePin(_ note: Note) {
        withAnimation {
            note.togglePin()
            do {
                try viewContext.save()
                HapticManager.shared.success()
            } catch {
                print("Error toggling pin: \(error)")
            }
        }
    }

    // MARK: - Sort Options

    enum SortOption: String, CaseIterable {
        case modifiedDate = "Değiştirilme Tarihi"
        case createdDate = "Oluşturma Tarihi"
        case title = "Başlık"
        case priority = "Öncelik"

        var displayName: String { rawValue }

        var icon: String {
            switch self {
            case .modifiedDate: return "clock"
            case .createdDate: return "calendar"
            case .title: return "textformat"
            case .priority: return "flag"
            }
        }
    }
}

// MARK: - Supporting Views

struct SearchBar: View {
    @Binding var text: String

    var body: some View {
        HStack {
            Image(systemName: "magnifyingglass")
                .foregroundColor(.secondary)

            TextField("Notlarda ara...", text: $text)
                .textFieldStyle(.plain)

            if !text.isEmpty {
                Button(action: { text = "" }) {
                    Image(systemName: "xmark.circle.fill")
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding(10)
        .background(Color.cardBackground)
        .cornerRadius(10)
    }
}

struct FilterChip: View {
    let title: String
    let icon: String
    var color: Color = .blue
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            HStack(spacing: 6) {
                Image(systemName: icon)
                    .font(.caption)
                Text(title)
                    .font(.subheadline)
                    .fontWeight(.medium)
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(isSelected ? color : Color.cardBackground)
            .foregroundColor(isSelected ? .white : .primary)
            .cornerRadius(20)
        }
    }
}

struct EmptyNotesView: View {
    let searchText: String

    var body: some View {
        VStack(spacing: 20) {
            Image(systemName: searchText.isEmpty ? "note.text" : "magnifyingglass")
                .font(.system(size: 60))
                .foregroundColor(.secondary)

            Text(searchText.isEmpty ? "Henüz not yok" : "Not bulunamadı")
                .font(.title3)
                .fontWeight(.semibold)

            Text(searchText.isEmpty ? "Yeni bir not eklemek için + butonuna dokun" : "Farklı bir arama terimi dene")
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
        }
        .padding(40)
    }
}
