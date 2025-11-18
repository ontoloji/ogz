//
//  NoteDetailView.swift
//  PersonalAssistant
//
//  Detail view for a single note
//

import SwiftUI

struct NoteDetailView: View {
    @ObservedObject var note: Note
    @Environment(\.managedObjectContext) private var viewContext
    @State private var isEditing = false

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                // Category and priority
                HStack {
                    if let category = note.category {
                        HStack(spacing: 6) {
                            Image(systemName: category.wrappedIconName)
                            Text(category.wrappedName)
                        }
                        .font(.subheadline)
                        .padding(.horizontal, 12)
                        .padding(.vertical, 6)
                        .background(category.categoryColor.opacity(0.2))
                        .foregroundColor(category.categoryColor)
                        .cornerRadius(8)
                    }

                    if note.priority > 0 {
                        HStack(spacing: 4) {
                            Image(systemName: note.priorityLevel.icon)
                            Text(note.priorityLevel.displayName)
                        }
                        .font(.subheadline)
                        .foregroundColor(note.priorityLevel.color)
                    }

                    Spacer()
                }

                // Title
                Text(note.wrappedTitle)
                    .font(.title)
                    .fontWeight(.bold)

                // Content
                Text(note.wrappedContent)
                    .font(.body)
                    .foregroundColor(.primary)

                // Reminder
                if let reminder = note.nextReminder {
                    HStack(spacing: 8) {
                        Image(systemName: "bell.fill")
                        Text("Hatırlatma: \(formatDate(reminder.date ?? Date()))")
                    }
                    .font(.subheadline)
                    .padding()
                    .background(Color.orange.opacity(0.1))
                    .foregroundColor(.orange)
                    .cornerRadius(10)
                }

                // Metadata
                VStack(alignment: .leading, spacing: 4) {
                    Text("Oluşturulma: \(formatDate(note.createdAt ?? Date()))")
                    Text("Değiştirilme: \(formatDate(note.modifiedAt ?? Date()))")
                }
                .font(.caption)
                .foregroundColor(.secondary)
            }
            .padding()
        }
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button(action: { isEditing = true }) {
                    Text("Düzenle")
                }
            }
        }
        .sheet(isPresented: $isEditing) {
            EditNoteView(note: note)
        }
    }

    private func formatDate(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateStyle = .medium
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

struct EditNoteView: View {
    @ObservedObject var note: Note
    @Environment(\.managedObjectContext) private var viewContext
    @Environment(\.dismiss) private var dismiss

    @State private var title: String
    @State private var content: String

    init(note: Note) {
        self.note = note
        _title = State(initialValue: note.wrappedTitle)
        _content = State(initialValue: note.wrappedContent)
    }

    var body: some View {
        NavigationView {
            Form {
                TextField("Başlık", text: $title)
                TextEditor(text: $content)
                    .frame(minHeight: 200)
            }
            .navigationTitle("Notu Düzenle")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("İptal") { dismiss() }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button("Kaydet") {
                        saveChanges()
                    }
                }
            }
        }
    }

    private func saveChanges() {
        note.update(title: title, content: content)
        do {
            try viewContext.save()
            HapticManager.shared.success()
            dismiss()
        } catch {
            print("Error saving: \(error)")
        }
    }
}

struct ArchivedNotesView: View {
    @Environment(\.managedObjectContext) private var viewContext
    @Environment(\.dismiss) private var dismiss

    @FetchRequest(
        fetchRequest: Note.archivedNotesFetchRequest(),
        animation: .default
    )
    private var archivedNotes: FetchedResults<Note>

    var body: some View {
        NavigationView {
            List {
                ForEach(archivedNotes) { note in
                    NoteCardView(note: note)
                        .swipeActions {
                            Button("Geri Al") {
                                unarchiveNote(note)
                            }
                            .tint(.green)

                            Button(role: .destructive) {
                                deleteNote(note)
                            } label: {
                                Label("Sil", systemImage: "trash")
                            }
                        }
                }
            }
            .navigationTitle("Arşivlenmiş Notlar")
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Bitti") { dismiss() }
                }
            }
        }
    }

    private func unarchiveNote(_ note: Note) {
        note.unarchive()
        try? viewContext.save()
        HapticManager.shared.success()
    }

    private func deleteNote(_ note: Note) {
        viewContext.delete(note)
        try? viewContext.save()
        HapticManager.shared.success()
    }
}
