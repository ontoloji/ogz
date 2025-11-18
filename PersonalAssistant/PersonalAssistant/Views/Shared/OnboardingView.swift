//
//  OnboardingView.swift
//  PersonalAssistant
//
//  Onboarding screen for first-time users
//

import SwiftUI

struct OnboardingView: View {
    @EnvironmentObject var appState: AppState
    @State private var currentPage = 0

    let pages: [OnboardingPage] = [
        OnboardingPage(
            image: "note.text",
            title: "Notlarını Organize Et",
            description: "Tüm notlarını tek yerden yönet, kategorize et ve kolayca ara."
        ),
        OnboardingPage(
            image: "bell.badge.fill",
            title: "Akıllı Hatırlatmalar",
            description: "Zamana ve konuma dayalı hatırlatmalarla hiçbir şeyi unutma."
        ),
        OnboardingPage(
            image: "calendar",
            title: "Takvim Entegrasyonu",
            description: "iOS takviminle senkronize ol, tüm etkinliklerini tek yerden takip et."
        ),
        OnboardingPage(
            image: "checkmark.circle.fill",
            title: "Görev Yönetimi",
            description: "Görevlerini yönet, ilerleme takibi yap ve hedeflerine ulaş."
        ),
        OnboardingPage(
            image: "chart.bar.fill",
            title: "Verimlilik Analizi",
            description: "Verimliliğini ölç, gelişimini takip et ve daha iyi ol."
        )
    ]

    var body: some View {
        VStack {
            // Skip button
            HStack {
                Spacer()
                Button("Atla") {
                    completeOnboarding()
                }
                .padding()
            }

            TabView(selection: $currentPage) {
                ForEach(pages.indices, id: \.self) { index in
                    OnboardingPageView(page: pages[index])
                        .tag(index)
                }
            }
            .tabViewStyle(.page(indexDisplayMode: .always))
            .indexViewStyle(.page(backgroundDisplayMode: .always))

            // Continue/Get Started button
            Button(action: {
                if currentPage < pages.count - 1 {
                    withAnimation {
                        currentPage += 1
                    }
                } else {
                    completeOnboarding()
                }
            }) {
                Text(currentPage < pages.count - 1 ? "Devam" : "Başla")
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.blue)
                    .cornerRadius(15)
            }
            .padding(.horizontal)
            .padding(.bottom, 30)
        }
    }

    private func completeOnboarding() {
        withAnimation {
            appState.completeOnboarding()
        }
        HapticManager.shared.success()
    }
}

struct OnboardingPage {
    let image: String
    let title: String
    let description: String
}

struct OnboardingPageView: View {
    let page: OnboardingPage

    var body: some View {
        VStack(spacing: 30) {
            Spacer()

            Image(systemName: page.image)
                .font(.system(size: 100))
                .foregroundColor(.blue)

            VStack(spacing: 15) {
                Text(page.title)
                    .font(.largeTitle)
                    .fontWeight(.bold)
                    .multilineTextAlignment(.center)

                Text(page.description)
                    .font(.body)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 40)
            }

            Spacer()
        }
    }
}
