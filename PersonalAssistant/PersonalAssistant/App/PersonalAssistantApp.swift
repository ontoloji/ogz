//
//  PersonalAssistantApp.swift
//  PersonalAssistant
//
//  Advanced Personal Assistant for iOS
//  Created with SwiftUI and modern iOS frameworks
//

import SwiftUI
import UserNotifications
import CoreData

@main
struct PersonalAssistantApp: App {
    // Core Data persistence controller
    @StateObject private var persistenceController = PersistenceController.shared

    // App-wide state management
    @StateObject private var appState = AppState()

    // Notification manager
    @StateObject private var notificationManager = NotificationManager.shared

    // Calendar manager
    @StateObject private var calendarManager = CalendarManager.shared

    // Location manager
    @StateObject private var locationManager = LocationManager.shared

    // Biometric authentication manager
    @StateObject private var biometricManager = BiometricAuthManager.shared

    @Environment(\.scenePhase) private var scenePhase

    init() {
        // Configure app appearance
        configureAppearance()

        // Request permissions
        requestPermissions()
    }

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(\.managedObjectContext, persistenceController.container.viewContext)
                .environmentObject(appState)
                .environmentObject(notificationManager)
                .environmentObject(calendarManager)
                .environmentObject(locationManager)
                .environmentObject(biometricManager)
                .onAppear {
                    setupApp()
                }
        }
        .onChange(of: scenePhase) { oldPhase, newPhase in
            handleScenePhaseChange(from: oldPhase, to: newPhase)
        }
    }

    // MARK: - Setup Methods

    private func configureAppearance() {
        // Configure navigation bar appearance
        let appearance = UINavigationBarAppearance()
        appearance.configureWithOpaqueBackground()
        UINavigationBar.appearance().standardAppearance = appearance
        UINavigationBar.appearance().scrollEdgeAppearance = appearance

        // Configure tab bar appearance
        let tabBarAppearance = UITabBarAppearance()
        tabBarAppearance.configureWithOpaqueBackground()
        UITabBar.appearance().standardAppearance = tabBarAppearance
        UITabBar.appearance().scrollEdgeAppearance = tabBarAppearance
    }

    private func requestPermissions() {
        // Request notification permissions
        Task {
            await notificationManager.requestAuthorization()
        }

        // Request calendar permissions
        Task {
            await calendarManager.requestAccess()
        }

        // Request location permissions (for location-based reminders)
        locationManager.requestWhenInUseAuthorization()
    }

    private func setupApp() {
        // Register for remote notifications if needed
        UIApplication.shared.registerForRemoteNotifications()

        // Configure background tasks
        BackgroundTaskManager.shared.registerBackgroundTasks()

        // Sync with iCloud if available
        if CloudKitManager.shared.isCloudKitAvailable {
            Task {
                await CloudKitManager.shared.syncWithCloud()
            }
        }

        // Schedule pending notifications
        Task {
            await notificationManager.schedulePendingNotifications()
        }
    }

    private func handleScenePhaseChange(from oldPhase: ScenePhase, to newPhase: ScenePhase) {
        switch newPhase {
        case .active:
            // App became active
            print("App became active")
            appState.refreshData()

        case .inactive:
            // App became inactive
            print("App became inactive")

        case .background:
            // App went to background
            print("App went to background")
            persistenceController.save()

        @unknown default:
            break
        }
    }
}

// MARK: - App State
class AppState: ObservableObject {
    @Published var selectedTab: Tab = .home
    @Published var showOnboarding: Bool = false
    @Published var isLocked: Bool = false

    enum Tab {
        case home
        case notes
        case calendar
        case tasks
        case analytics
        case settings
    }

    init() {
        // Check if user has completed onboarding
        showOnboarding = !UserDefaults.standard.bool(forKey: "hasCompletedOnboarding")

        // Check if biometric lock is enabled
        if UserDefaults.standard.bool(forKey: "isBiometricLockEnabled") {
            isLocked = true
        }
    }

    func refreshData() {
        // Refresh app data when becoming active
        NotificationCenter.default.post(name: .refreshData, object: nil)
    }

    func completeOnboarding() {
        UserDefaults.standard.set(true, forKey: "hasCompletedOnboarding")
        showOnboarding = false
    }
}

// MARK: - Notification Names
extension Notification.Name {
    static let refreshData = Notification.Name("refreshData")
    static let syncCompleted = Notification.Name("syncCompleted")
    static let locationReminderTriggered = Notification.Name("locationReminderTriggered")
}
