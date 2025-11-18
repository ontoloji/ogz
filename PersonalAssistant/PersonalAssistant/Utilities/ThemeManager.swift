//
//  ThemeManager.swift
//  PersonalAssistant
//
//  Manages app theme and appearance
//

import SwiftUI

class ThemeManager: ObservableObject {
    static let shared = ThemeManager()

    @Published var colorScheme: ColorScheme? {
        didSet {
            UserDefaults.standard.set(colorScheme?.rawValue, forKey: "colorScheme")
        }
    }

    @Published var accentColor: Color {
        didSet {
            if let hex = accentColor.toHex() {
                UserDefaults.standard.set(hex, forKey: "accentColor")
            }
        }
    }

    init() {
        // Load saved color scheme
        if let rawValue = UserDefaults.standard.string(forKey: "colorScheme"),
           let scheme = ColorScheme(rawValue: rawValue) {
            colorScheme = scheme
        } else {
            colorScheme = nil // System default
        }

        // Load saved accent color
        if let hex = UserDefaults.standard.string(forKey: "accentColor"),
           let color = Color(hex: hex) {
            accentColor = color
        } else {
            accentColor = .blue
        }
    }

    func setColorScheme(_ scheme: AppearanceMode) {
        switch scheme {
        case .system:
            colorScheme = nil
        case .light:
            colorScheme = .light
        case .dark:
            colorScheme = .dark
        }
    }

    enum AppearanceMode: String, CaseIterable {
        case system = "Sistem"
        case light = "Açık"
        case dark = "Koyu"

        var icon: String {
            switch self {
            case .system: return "circle.lefthalf.filled"
            case .light: return "sun.max.fill"
            case .dark: return "moon.fill"
            }
        }
    }
}

// MARK: - Color Scheme Extension

extension ColorScheme {
    var rawValue: String {
        switch self {
        case .light: return "light"
        case .dark: return "dark"
        @unknown default: return "light"
        }
    }

    init?(rawValue: String) {
        switch rawValue {
        case "light": self = .light
        case "dark": self = .dark
        default: return nil
        }
    }
}

// MARK: - App Colors

extension Color {
    // Priority colors
    static let lowPriority = Color.green
    static let normalPriority = Color.blue
    static let highPriority = Color.red

    // Category colors
    static let categoryWork = Color(hex: "#FF6B6B")!
    static let categoryPersonal = Color(hex: "#4ECDC4")!
    static let categoryShopping = Color(hex: "#95E1D3")!
    static let categoryHealth = Color(hex: "#F38181")!
    static let categoryEducation = Color(hex: "#AA96DA")!
    static let categoryFinance = Color(hex: "#FCBAD3")!
    static let categoryTravel = Color(hex: "#FFFFD2")!
    static let categoryHobby = Color(hex: "#A8D8EA")!

    // Status colors
    static let successColor = Color.green
    static let warningColor = Color.orange
    static let errorColor = Color.red
    static let infoColor = Color.blue

    // Background colors
    static let cardBackground = Color(UIColor.secondarySystemGroupedBackground)
    static let screenBackground = Color(UIColor.systemGroupedBackground)
}
