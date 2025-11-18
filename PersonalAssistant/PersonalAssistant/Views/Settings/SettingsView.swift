//
//  SettingsView.swift
//  PersonalAssistant
//
//  Settings and preferences view
//

import SwiftUI

struct SettingsView: View {
    @EnvironmentObject var biometricManager: BiometricAuthManager
    @StateObject private var themeManager = ThemeManager.shared
    @State private var showingAbout = false

    var body: some View {
        NavigationView {
            Form {
                // Appearance Section
                Section("Görünüm") {
                    Picker("Tema", selection: $themeManager.colorScheme) {
                        ForEach(ThemeManager.AppearanceMode.allCases, id: \.self) { mode in
                            HStack {
                                Image(systemName: mode.icon)
                                Text(mode.rawValue)
                            }
                            .tag(mode == .system ? nil as ColorScheme? : (mode == .light ? .light as ColorScheme? : .dark as ColorScheme?))
                        }
                    }

                    ColorPicker("Vurgu Rengi", selection: $themeManager.accentColor)
                }

                // Security Section
                Section("Güvenlik") {
                    if biometricManager.biometricType != .none {
                        Toggle(isOn: $biometricManager.isBiometricEnabled) {
                            HStack {
                                Image(systemName: biometricManager.biometricType.icon)
                                Text("\(biometricManager.biometricType.displayName) Kilidi")
                            }
                        }

                        Text("Uygulama açıldığında \(biometricManager.biometricType.displayName) ile doğrulama iste")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }

                // Notifications Section
                Section("Bildirimler") {
                    NavigationLink("Bildirim Ayarları") {
                        NotificationSettingsView()
                    }

                    NavigationLink("Hatırlatma Varsayılanları") {
                        ReminderDefaultsView()
                    }
                }

                // Data & Sync Section
                Section("Veri ve Senkronizasyon") {
                    NavigationLink("iCloud Senkronizasyonu") {
                        CloudSyncSettingsView()
                    }

                    Button("Verileri Dışa Aktar") {
                        exportData()
                    }

                    Button("Önbelleği Temizle") {
                        clearCache()
                    }
                }

                // Categories Section
                Section("Kategoriler") {
                    NavigationLink("Kategorileri Yönet") {
                        ManageCategoriesView()
                    }
                }

                // About Section
                Section("Hakkında") {
                    HStack {
                        Text("Versiyon")
                        Spacer()
                        Text("1.0.0")
                            .foregroundColor(.secondary)
                    }

                    Button("Gizlilik Politikası") {
                        // Open privacy policy
                    }

                    Button("Kullanım Koşulları") {
                        // Open terms
                    }

                    NavigationLink("Hakkında") {
                        AboutView()
                    }
                }

                // Danger Zone
                Section("Tehlike Bölgesi") {
                    Button(role: .destructive, action: deleteAllData) {
                        Text("Tüm Verileri Sil")
                    }
                }
            }
            .navigationTitle("Ayarlar")
        }
    }

    private func exportData() {
        // Implement data export
        HapticManager.shared.success()
    }

    private func clearCache() {
        // Implement cache clearing
        HapticManager.shared.success()
    }

    private func deleteAllData() {
        // Implement data deletion with confirmation
    }
}

struct NotificationSettingsView: View {
    @State private var notificationsEnabled = true
    @State private var soundEnabled = true
    @State private var badgeEnabled = true

    var body: some View {
        Form {
            Toggle("Bildirimleri Etkinleştir", isOn: $notificationsEnabled)
            Toggle("Ses", isOn: $soundEnabled)
            Toggle("Rozet", isOn: $badgeEnabled)

            Section("Bildirim Zamanı") {
                Text("Sessiz saatlerde bildirim gösterme")
            }
        }
        .navigationTitle("Bildirimler")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct ReminderDefaultsView: View {
    @State private var defaultReminderTime = Date()

    var body: some View {
        Form {
            Section("Varsayılan Hatırlatma Saati") {
                DatePicker("Saat", selection: $defaultReminderTime, displayedComponents: .hourAndMinute)
            }

            Section("Hatırlatma Seçenekleri") {
                Toggle("Konum Tabanlı Hatırlatmaları Etkinleştir", isOn: .constant(true))
            }
        }
        .navigationTitle("Hatırlatma Ayarları")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct CloudSyncSettingsView: View {
    @EnvironmentObject var cloudManager: CloudKitManager

    var body: some View {
        Form {
            Section {
                HStack {
                    Text("Durum")
                    Spacer()
                    if cloudManager.isSyncing {
                        ProgressView()
                    } else {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.green)
                    }
                }

                Text(cloudManager.syncStatusText)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            Section {
                Button("Manuel Senkronize Et") {
                    Task {
                        await cloudManager.syncWithCloud()
                    }
                }
            }

            Section("Bilgi") {
                Text("iCloud üzerinden tüm cihazlarınızda verileriniz otomatik olarak senkronize edilir.")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .navigationTitle("iCloud Sync")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct ManageCategoriesView: View {
    @Environment(\.managedObjectContext) private var viewContext

    @FetchRequest(
        fetchRequest: Category.allCategoriesFetchRequest(),
        animation: .default
    )
    private var categories: FetchedResults<Category>

    @State private var showingAddCategory = false

    var body: some View {
        List {
            ForEach(categories) { category in
                HStack {
                    Image(systemName: category.wrappedIconName)
                        .foregroundColor(category.categoryColor)

                    Text(category.wrappedName)

                    Spacer()

                    Text("\(category.notesCount) not")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .onDelete(perform: deleteCategories)
        }
        .navigationTitle("Kategoriler")
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Button(action: { showingAddCategory = true }) {
                    Image(systemName: "plus")
                }
            }
        }
        .sheet(isPresented: $showingAddCategory) {
            AddCategoryView()
        }
    }

    private func deleteCategories(at offsets: IndexSet) {
        offsets.forEach { index in
            viewContext.delete(categories[index])
        }
        try? viewContext.save()
    }
}

struct AddCategoryView: View {
    @Environment(\.managedObjectContext) private var viewContext
    @Environment(\.dismiss) private var dismiss

    @State private var name = ""
    @State private var selectedColor = Color.blue
    @State private var selectedIcon = "folder"

    private let availableIcons = ["folder", "briefcase", "cart", "heart.fill", "book.fill", "house.fill"]

    var body: some View {
        NavigationView {
            Form {
                TextField("Kategori Adı", text: $name)

                ColorPicker("Renk", selection: $selectedColor)

                Section("İkon") {
                    LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 6)) {
                        ForEach(availableIcons, id: \.self) { icon in
                            Image(systemName: icon)
                                .font(.title2)
                                .foregroundColor(selectedIcon == icon ? selectedColor : .gray)
                                .frame(width: 44, height: 44)
                                .background(selectedIcon == icon ? selectedColor.opacity(0.2) : Color.clear)
                                .cornerRadius(8)
                                .onTapGesture {
                                    selectedIcon = icon
                                }
                        }
                    }
                }
            }
            .navigationTitle("Yeni Kategori")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button("İptal") { dismiss() }
                }

                ToolbarItem(placement: .confirmationAction) {
                    Button("Kaydet") {
                        saveCategory()
                    }
                    .disabled(name.isEmpty)
                }
            }
        }
    }

    private func saveCategory() {
        _ = Category.create(
            in: viewContext,
            name: name,
            colorHex: selectedColor.toHex() ?? "#007AFF",
            iconName: selectedIcon
        )

        try? viewContext.save()
        HapticManager.shared.success()
        dismiss()
    }
}

struct AboutView: View {
    var body: some View {
        ScrollView {
            VStack(spacing: 30) {
                Image(systemName: "note.text.badge.plus")
                    .font(.system(size: 80))
                    .foregroundColor(.blue)

                Text("Personal Assistant")
                    .font(.title)
                    .fontWeight(.bold)

                Text("Version 1.0.0")
                    .font(.subheadline)
                    .foregroundColor(.secondary)

                Text("Hayatını organize et, hedeflerine ulaş.")
                    .font(.body)
                    .multilineTextAlignment(.center)
                    .padding()

                VStack(spacing: 15) {
                    FeatureRow(icon: "note.text", title: "Notlar", description: "Tüm notlarını tek yerden yönet")
                    FeatureRow(icon: "checkmark.circle", title: "Görevler", description: "Görevlerini takip et ve tamamla")
                    FeatureRow(icon: "calendar", title: "Takvim", description: "Etkinliklerini planla")
                    FeatureRow(icon: "chart.bar", title: "Analitik", description: "Verimliliğini ölç")
                }
                .padding()
            }
            .padding()
        }
        .navigationTitle("Hakkında")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct FeatureRow: View {
    let icon: String
    let title: String
    let description: String

    var body: some View {
        HStack(spacing: 15) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundColor(.blue)
                .frame(width: 40)

            VStack(alignment: .leading, spacing: 4) {
                Text(title)
                    .font(.headline)
                Text(description)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }

            Spacer()
        }
    }
}
