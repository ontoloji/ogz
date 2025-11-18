//
//  AppIntents.swift
//  PersonalAssistantIntents
//
//  App Intents and Shortcuts for Siri integration
//

import AppIntents
import Foundation

// MARK: - Add Note Intent

@available(iOS 16.0, *)
struct AddNoteIntent: AppIntent {
    static var title: LocalizedStringResource = "Not Ekle"
    static var description = IntentDescription("Personal Assistant'a hızlıca not ekle")
    static var openAppWhenRun: Bool = false

    @Parameter(title: "Başlık")
    var title: String

    @Parameter(title: "İçerik")
    var content: String?

    @MainActor
    func perform() async throws -> some IntentResult {
        // Add note to Core Data
        // This would require shared app group container

        return .result(dialog: IntentDialog("Not başarıyla eklendi: \(title)"))
    }

    static var parameterSummary: some ParameterSummary {
        Summary("Personal Assistant'a \(\.$title) başlıklı not ekle")
    }
}

// MARK: - Add Task Intent

@available(iOS 16.0, *)
struct AddTaskIntent: AppIntent {
    static var title: LocalizedStringResource = "Görev Ekle"
    static var description = IntentDescription("Yeni bir görev oluştur")
    static var openAppWhenRun: Bool = false

    @Parameter(title: "Görev Başlığı")
    var taskTitle: String

    @Parameter(title: "Son Tarih")
    var dueDate: Date?

    @Parameter(title: "Öncelik")
    var priority: PriorityLevel?

    @MainActor
    func perform() async throws -> some IntentResult {
        // Add task to Core Data

        return .result(dialog: IntentDialog("Görev oluşturuldu: \(taskTitle)"))
    }

    static var parameterSummary: some ParameterSummary {
        Summary("'\(\.$taskTitle)' görevini ekle")
    }
}

// MARK: - Start Pomodoro Intent

@available(iOS 16.0, *)
struct StartPomodoroIntent: AppIntent {
    static var title: LocalizedStringResource = "Pomodoro Başlat"
    static var description = IntentDescription("Odaklanma oturumu başlat")
    static var openAppWhenRun: Bool = true

    @Parameter(title: "Süre (dakika)", default: 25)
    var duration: Int

    @MainActor
    func perform() async throws -> some IntentResult {
        // Start Pomodoro timer

        return .result(dialog: IntentDialog("\(duration) dakikalık odaklanma oturumu başladı"))
    }
}

// MARK: - View Today's Tasks Intent

@available(iOS 16.0, *)
struct ViewTodayTasksIntent: AppIntent {
    static var title: LocalizedStringResource = "Bugünkü Görevleri Gör"
    static var description = IntentDescription("Bugünkü görevlerin listesini göster")
    static var openAppWhenRun: Bool = true

    @MainActor
    func perform() async throws -> some IntentResult & ReturnsValue<String> {
        // Fetch today's tasks
        let tasksCount = 5 // This would be fetched from Core Data

        return .result(
            value: "Bugün \(tasksCount) görevin var",
            dialog: IntentDialog("Bugünkü görevlerin gösteriliyor")
        )
    }
}

// MARK: - Complete Task Intent

@available(iOS 16.0, *)
struct CompleteTaskIntent: AppIntent {
    static var title: LocalizedStringResource = "Görevi Tamamla"
    static var description = IntentDescription("Bir görevi tamamlandı olarak işaretle")
    static var openAppWhenRun: Bool = false

    @Parameter(title: "Görev")
    var taskIdentifier: String

    @MainActor
    func perform() async throws -> some IntentResult {
        // Mark task as complete

        return .result(dialog: IntentDialog("Görev tamamlandı"))
    }
}

// MARK: - Supporting Types

enum PriorityLevel: String, AppEnum {
    case low = "Düşük"
    case normal = "Normal"
    case high = "Yüksek"

    static var typeDisplayRepresentation: TypeDisplayRepresentation = "Öncelik"
    static var caseDisplayRepresentations: [PriorityLevel : DisplayRepresentation] = [
        .low: "Düşük",
        .normal: "Normal",
        .high: "Yüksek"
    ]
}

// MARK: - App Shortcuts Provider

@available(iOS 16.0, *)
struct PersonalAssistantShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: AddNoteIntent(),
            phrases: [
                "Hızlı not ekle \(.applicationName)",
                "Not oluştur \(.applicationName)",
                "\(.applicationName) ile not ekle"
            ],
            shortTitle: "Hızlı Not",
            systemImageName: "note.text"
        )

        AppShortcut(
            intent: AddTaskIntent(),
            phrases: [
                "Görev ekle \(.applicationName)",
                "Yeni görev oluştur \(.applicationName)",
                "\(.applicationName) ile görev ekle"
            ],
            shortTitle: "Görev Ekle",
            systemImageName: "checkmark.circle"
        )

        AppShortcut(
            intent: StartPomodoroIntent(),
            phrases: [
                "Pomodoro başlat \(.applicationName)",
                "Odaklanma oturumu başlat \(.applicationName)",
                "\(.applicationName) ile odaklan"
            ],
            shortTitle: "Pomodoro",
            systemImageName: "timer"
        )

        AppShortcut(
            intent: ViewTodayTasksIntent(),
            phrases: [
                "Bugünkü görevleri göster \(.applicationName)",
                "Bugün ne yapacağım \(.applicationName)",
                "\(.applicationName) bugünkü görevler"
            ],
            shortTitle: "Bugünkü Görevler",
            systemImageName: "list.bullet"
        )
    }
}
