//
//  PomodoroTimerView.swift
//  PersonalAssistant
//
//  Pomodoro timer for focus sessions
//

import SwiftUI

struct PomodoroTimerView: View {
    @Environment(\.dismiss) private var dismiss
    @StateObject private var timerManager = PomodoroTimerManager()

    var body: some View {
        NavigationView {
            VStack(spacing: 40) {
                // Timer Type
                Picker("Mod", selection: $timerManager.timerType) {
                    ForEach(PomodoroTimerManager.TimerType.allCases, id: \.self) { type in
                        Text(type.displayName).tag(type)
                    }
                }
                .pickerStyle(.segmented)
                .padding()
                .disabled(timerManager.isRunning)

                Spacer()

                // Circular Progress
                ZStack {
                    Circle()
                        .stroke(Color.gray.opacity(0.2), lineWidth: 20)
                        .frame(width: 250, height: 250)

                    Circle()
                        .trim(from: 0, to: timerManager.progress)
                        .stroke(timerManager.timerType.color, style: StrokeStyle(lineWidth: 20, lineCap: .round))
                        .frame(width: 250, height: 250)
                        .rotationEffect(.degrees(-90))
                        .animation(.linear(duration: 0.5), value: timerManager.progress)

                    VStack(spacing: 10) {
                        Text(timerManager.timeString)
                            .font(.system(size: 50, weight: .bold, design: .rounded))
                            .monospacedDigit()

                        Text(timerManager.timerType.displayName)
                            .font(.headline)
                            .foregroundColor(.secondary)
                    }
                }

                Spacer()

                // Control Buttons
                HStack(spacing: 30) {
                    if timerManager.isRunning {
                        // Pause Button
                        Button(action: {
                            timerManager.pauseTimer()
                        }) {
                            Image(systemName: "pause.fill")
                                .font(.title)
                                .frame(width: 70, height: 70)
                                .background(Color.orange)
                                .foregroundColor(.white)
                                .clipShape(Circle())
                        }

                        // Stop Button
                        Button(action: {
                            timerManager.stopTimer()
                        }) {
                            Image(systemName: "stop.fill")
                                .font(.title)
                                .frame(width: 70, height: 70)
                                .background(Color.red)
                                .foregroundColor(.white)
                                .clipShape(Circle())
                        }
                    } else {
                        // Start/Resume Button
                        Button(action: {
                            timerManager.startTimer()
                        }) {
                            Image(systemName: timerManager.isPaused ? "play.fill" : "play.fill")
                                .font(.title)
                                .frame(width: 100, height: 100)
                                .background(Color.green)
                                .foregroundColor(.white)
                                .clipShape(Circle())
                        }
                    }
                }

                // Session Stats
                HStack(spacing: 40) {
                    VStack {
                        Text("\(timerManager.completedSessions)")
                            .font(.title2)
                            .fontWeight(.bold)
                        Text("Tamamlanan")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }

                    VStack {
                        Text("\(timerManager.totalMinutes)")
                            .font(.title2)
                            .fontWeight(.bold)
                        Text("Dakika")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                .padding()
                .background(Color.cardBackground)
                .cornerRadius(15)

                Spacer()
            }
            .navigationTitle("Pomodoro Timer")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .confirmationAction) {
                    Button("Bitti") { dismiss() }
                }
            }
        }
    }
}

// MARK: - Pomodoro Timer Manager

class PomodoroTimerManager: ObservableObject {
    @Published var timeRemaining: Int = 1500 // 25 minutes
    @Published var isRunning = false
    @Published var isPaused = false
    @Published var timerType: TimerType = .focus {
        didSet {
            if !isRunning {
                timeRemaining = timerType.duration
            }
        }
    }

    @Published var completedSessions = 0
    @Published var totalMinutes = 0

    private var timer: Timer?
    private var totalDuration: Int

    var progress: Double {
        return Double(totalDuration - timeRemaining) / Double(totalDuration)
    }

    var timeString: String {
        let minutes = timeRemaining / 60
        let seconds = timeRemaining % 60
        return String(format: "%02d:%02d", minutes, seconds)
    }

    init() {
        totalDuration = timerType.duration
    }

    func startTimer() {
        guard !isRunning else { return }

        isRunning = true
        isPaused = false

        if timeRemaining == timerType.duration {
            totalDuration = timerType.duration
        }

        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            guard let self = self else { return }

            if self.timeRemaining > 0 {
                self.timeRemaining -= 1
            } else {
                self.timerCompleted()
            }
        }
    }

    func pauseTimer() {
        isRunning = false
        isPaused = true
        timer?.invalidate()
        timer = nil
    }

    func stopTimer() {
        isRunning = false
        isPaused = false
        timer?.invalidate()
        timer = nil
        timeRemaining = timerType.duration
        totalDuration = timerType.duration
    }

    private func timerCompleted() {
        isRunning = false
        timer?.invalidate()
        timer = nil

        if timerType == .focus {
            completedSessions += 1
            totalMinutes += 25
        }

        // Send notification
        HapticManager.shared.success()

        // Auto-switch to break
        if timerType == .focus {
            timerType = completedSessions % 4 == 0 ? .longBreak : .shortBreak
        } else {
            timerType = .focus
        }

        timeRemaining = timerType.duration
        totalDuration = timerType.duration
    }

    enum TimerType: CaseIterable {
        case focus
        case shortBreak
        case longBreak

        var displayName: String {
            switch self {
            case .focus: return "Odaklanma"
            case .shortBreak: return "Kısa Mola"
            case .longBreak: return "Uzun Mola"
            }
        }

        var duration: Int {
            switch self {
            case .focus: return 1500 // 25 minutes
            case .shortBreak: return 300 // 5 minutes
            case .longBreak: return 900 // 15 minutes
            }
        }

        var color: Color {
            switch self {
            case .focus: return .blue
            case .shortBreak: return .green
            case .longBreak: return .purple
            }
        }
    }
}
