//
//  AddNoteView.swift
//  PersonalAssistant
//
//  View for adding new notes
//

import SwiftUI

struct AddNoteView: View {
    @Environment(\.managedObjectContext) private var viewContext
    @Environment(\.dismiss) private var dismiss

    @State private var title = ""
    @State private var content = ""
    @State private var selectedCategory: Category?
    @State private var priority: Note.Priority = .normal
    @State private var hasReminder = false
    @State private var reminderDate = Date()

    @FetchRequest(
        fetchRequest: Category.allCategoriesFetchRequest(),
        animation: .default
    )
    private var categories: FetchedResults<Category>

    var body: some View {
        NavigationView {
            Form {
                Section("Temel Bilgiler") {
                    TextField("Başlık", text: $title)
                    TextEditor(text: $content)
                        .frame(minHeight: 100)
                }

                Section("Kategori") {
                    Picker("Kategori", selection: $selectedCategory) {
                        Text("Kategori seçiniz").tag(nil as Category?)
                        ForEach(categories) { category in
                            HStack {
                                Image(systemName: category.wrappedIconName)
                                Text(category.wrappedName)
                            }
                            .tag(category as Category?)
                        }
                    }
                }

                Section("Öncelik") {
                    Picker("Öncelik", selection: $priority) {
                        ForEach(Note.Priority.allCases, id: \.self) { priority in
                            HStack {
                                Image(systemName: priority.icon)
                                Text(priority.displayName)
                            }
                            .tag(priority)
                        }
                    }
                    .pickerStyle(.segmented)
                }

                Section("Hatırlatma") {
                    Toggle("Hatırlatma ekle", isOn: $hasReminder)

                    if hasReminder {
                        DatePicker("Tarih ve Saat", selection: $reminderDate, in: Date()...)
                    }
                }
            }
            .navigationTitle("Yeni Not")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("İptal") {
                        dismiss()
                    }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button("Kaydet") {
                        saveNote()
                    }
                    .disabled(title.isEmpty)
                }
            }
        }
    }

    private func saveNote() {
        let note = Note.create(
            in: viewContext,
            title: title,
            content: content,
            category: selectedCategory,
            priority: priority
        )

        if hasReminder {
            note.addReminder(date: reminderDate, in: viewContext)

            // Schedule notification
            Task {
                try? await NotificationManager.shared.scheduleNotification(
                    id: note.id!.uuidString,
                    title: title,
                    body: content.isEmpty ? "Hatırlatma" : content,
                    date: reminderDate,
                    categoryIdentifier: "REMINDER"
                )
            }
        }

        do {
            try viewContext.save()
            HapticManager.shared.success()
            dismiss()
        } catch {
            print("Error saving note: \(error)")
        }
    }
}
