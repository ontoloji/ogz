//
//  BiometricAuthManager.swift
//  PersonalAssistant
//
//  Manages biometric authentication (Face ID / Touch ID)
//

import Foundation
import LocalAuthentication
import SwiftUI

@MainActor
class BiometricAuthManager: ObservableObject {
    static let shared = BiometricAuthManager()

    @Published var biometricType: BiometricType = .none
    @Published var isAuthenticated = false
    @Published var isBiometricEnabled: Bool {
        didSet {
            UserDefaults.standard.set(isBiometricEnabled, forKey: "isBiometricLockEnabled")
        }
    }

    private let context = LAContext()

    init() {
        isBiometricEnabled = UserDefaults.standard.bool(forKey: "isBiometricLockEnabled")
        checkBiometricAvailability()
    }

    // MARK: - Check Availability

    func checkBiometricAvailability() {
        var error: NSError?

        if context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) {
            switch context.biometryType {
            case .faceID:
                biometricType = .faceID
            case .touchID:
                biometricType = .touchID
            default:
                biometricType = .none
            }
        } else {
            biometricType = .none
            print("Biometric authentication not available: \(error?.localizedDescription ?? "Unknown error")")
        }
    }

    // MARK: - Authentication

    func authenticate(reason: String = "Uygulamayı açmak için kimliğinizi doğrulayın") async -> Bool {
        let context = LAContext()
        context.localizedCancelTitle = "İptal"
        context.localizedFallbackTitle = "Şifre Kullan"

        var error: NSError?

        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
            print("Biometric auth not available: \(error?.localizedDescription ?? "Unknown")")
            // Fall back to passcode
            return await authenticateWithPasscode()
        }

        do {
            let success = try await context.evaluatePolicy(
                .deviceOwnerAuthenticationWithBiometrics,
                localizedReason: reason
            )

            await MainActor.run {
                isAuthenticated = success
            }

            return success
        } catch let error as LAError {
            print("Biometric auth error: \(error.localizedDescription)")

            switch error.code {
            case .userFallback:
                // User chose to use passcode
                return await authenticateWithPasscode()
            case .userCancel:
                // User cancelled
                return false
            case .biometryNotAvailable:
                // Biometry not available, try passcode
                return await authenticateWithPasscode()
            default:
                return false
            }
        } catch {
            print("Unexpected error: \(error)")
            return false
        }
    }

    private func authenticateWithPasscode() async -> Bool {
        let context = LAContext()

        do {
            let success = try await context.evaluatePolicy(
                .deviceOwnerAuthentication,
                localizedReason: "Şifrenizi girin"
            )

            await MainActor.run {
                isAuthenticated = success
            }

            return success
        } catch {
            print("Passcode auth error: \(error)")
            return false
        }
    }

    // MARK: - Lock/Unlock

    func lockApp() {
        isAuthenticated = false
    }

    func unlockApp() async -> Bool {
        if isBiometricEnabled {
            return await authenticate()
        } else {
            isAuthenticated = true
            return true
        }
    }

    // MARK: - Secure Note Authentication

    func authenticateForSecureNote() async -> Bool {
        return await authenticate(reason: "Güvenli nota erişmek için kimliğinizi doğrulayın")
    }

    // MARK: - Enable/Disable

    func enableBiometric() {
        isBiometricEnabled = true
    }

    func disableBiometric() {
        isBiometricEnabled = false
        isAuthenticated = true
    }

    // MARK: - Biometric Type

    enum BiometricType {
        case none
        case faceID
        case touchID

        var displayName: String {
            switch self {
            case .none: return "Yok"
            case .faceID: return "Face ID"
            case .touchID: return "Touch ID"
            }
        }

        var icon: String {
            switch self {
            case .none: return "lock.slash"
            case .faceID: return "faceid"
            case .touchID: return "touchid"
            }
        }
    }
}
