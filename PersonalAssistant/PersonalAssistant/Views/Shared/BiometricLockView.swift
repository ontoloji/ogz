//
//  BiometricLockView.swift
//  PersonalAssistant
//
//  Biometric lock screen
//

import SwiftUI

struct BiometricLockView: View {
    @EnvironmentObject var appState: AppState
    @EnvironmentObject var biometricManager: BiometricAuthManager
    @State private var showError = false
    @State private var errorMessage = ""

    var body: some View {
        ZStack {
            // Background gradient
            LinearGradient(
                gradient: Gradient(colors: [.blue.opacity(0.6), .purple.opacity(0.6)]),
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
            .ignoresSafeArea()

            VStack(spacing: 40) {
                Spacer()

                // Lock icon
                Image(systemName: biometricManager.biometricType == .faceID ? "faceid" : "touchid")
                    .font(.system(size: 80))
                    .foregroundColor(.white)

                VStack(spacing: 15) {
                    Text("Personal Assistant")
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(.white)

                    Text("Devam etmek için kimliğinizi doğrulayın")
                        .font(.body)
                        .foregroundColor(.white.opacity(0.8))
                        .multilineTextAlignment(.center)
                }

                // Unlock button
                Button(action: {
                    authenticate()
                }) {
                    HStack {
                        Image(systemName: biometricManager.biometricType.icon)
                        Text("Kilidi Aç")
                    }
                    .font(.headline)
                    .foregroundColor(.blue)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.white)
                    .cornerRadius(15)
                }
                .padding(.horizontal, 40)

                if showError {
                    Text(errorMessage)
                        .font(.caption)
                        .foregroundColor(.red)
                        .padding()
                        .background(Color.white.opacity(0.9))
                        .cornerRadius(10)
                        .padding(.horizontal, 40)
                }

                Spacer()
            }
        }
        .onAppear {
            authenticate()
        }
    }

    private func authenticate() {
        Task {
            let success = await biometricManager.unlockApp()

            await MainActor.run {
                if success {
                    appState.isLocked = false
                    HapticManager.shared.success()
                } else {
                    showError = true
                    errorMessage = "Kimlik doğrulama başarısız. Lütfen tekrar deneyin."
                    HapticManager.shared.error()
                }
            }
        }
    }
}
