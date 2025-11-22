import SwiftUI

struct ContentView: View {
    @EnvironmentObject var dataManager: DataManager
    @State private var selectedTab = 0

    var body: some View {
        Group {
            if dataManager.userProfile == nil {
                ProfileSetupView()
            } else {
                TabView(selection: $selectedTab) {
                    HomeView()
                        .tabItem {
                            Label("Ana Sayfa", systemImage: "house.fill")
                        }
                        .tag(0)

                    WorkoutPlanView()
                        .tabItem {
                            Label("Program", systemImage: "list.bullet.clipboard.fill")
                        }
                        .tag(1)

                    ProgressView()
                        .tabItem {
                            Label("İlerleme", systemImage: "chart.line.uptrend.xyaxis")
                        }
                        .tag(2)

                    SettingsView()
                        .tabItem {
                            Label("Ayarlar", systemImage: "gearshape.fill")
                        }
                        .tag(3)
                }
                .accentColor(.blue)
            }
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(DataManager())
}
