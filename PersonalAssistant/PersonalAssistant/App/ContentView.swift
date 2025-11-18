//
//  ContentView.swift
//  PersonalAssistant
//
//  Main content view with tab navigation
//

import SwiftUI

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var biometricManager: BiometricAuthManager
    @State private var selectedTab = 0

    var body: some View {
        Group {
            if appState.showOnboarding {
                OnboardingView()
            } else if appState.isLocked {
                BiometricLockView()
            } else {
                mainContent
            }
        }
        .preferredColorScheme(ThemeManager.shared.colorScheme)
    }

    private var mainContent: some View {
        TabView(selection: $selectedTab) {
            // Home Dashboard
            HomeView()
                .tabItem {
                    Label("Ana Sayfa", systemImage: "house.fill")
                }
                .tag(0)

            // Notes
            NotesListView()
                .tabItem {
                    Label("Notlar", systemImage: "note.text")
                }
                .tag(1)

            // Calendar
            CalendarView()
                .tabItem {
                    Label("Takvim", systemImage: "calendar")
                }
                .tag(2)

            // Tasks
            TasksView()
                .tabItem {
                    Label("Görevler", systemImage: "checkmark.circle.fill")
                }
                .tag(3)

            // Analytics
            AnalyticsView()
                .tabItem {
                    Label("Analitik", systemImage: "chart.bar.fill")
                }
                .tag(4)

            // Settings
            SettingsView()
                .tabItem {
                    Label("Ayarlar", systemImage: "gear")
                }
                .tag(5)
        }
        .accentColor(.blue)
        .onAppear {
            // Haptic feedback when switching tabs
            UITabBar.appearance().isTranslucent = true
        }
    }
}

// MARK: - Preview
struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .environmentObject(AppState())
            .environmentObject(BiometricAuthManager.shared)
            .environment(\.managedObjectContext, PersistenceController.preview.container.viewContext)
    }
}
