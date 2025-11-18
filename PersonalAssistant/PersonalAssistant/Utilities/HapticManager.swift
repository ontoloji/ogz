//
//  HapticManager.swift
//  PersonalAssistant
//
//  Manages haptic feedback
//

import UIKit

class HapticManager {
    static let shared = HapticManager()

    private init() {}

    func impact(_ style: UIImpactFeedbackGenerator.FeedbackStyle) {
        let generator = UIImpactFeedbackGenerator(style: style)
        generator.impactOccurred()
    }

    func notification(_ type: UINotificationFeedbackGenerator.FeedbackType) {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(type)
    }

    func selection() {
        let generator = UISelectionFeedbackGenerator()
        generator.selectionChanged()
    }

    // Convenience methods
    func success() {
        notification(.success)
    }

    func warning() {
        notification(.warning)
    }

    func error() {
        notification(.error)
    }

    func lightImpact() {
        impact(.light)
    }

    func mediumImpact() {
        impact(.medium)
    }

    func heavyImpact() {
        impact(.heavy)
    }

    func softImpact() {
        if #available(iOS 13.0, *) {
            impact(.soft)
        } else {
            impact(.light)
        }
    }

    func rigidImpact() {
        if #available(iOS 13.0, *) {
            impact(.rigid)
        } else {
            impact(.heavy)
        }
    }
}
