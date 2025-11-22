#include "NetworkInterface.h"
#include "PacketCapture.h"
#include "PacketAnalyzer.h"
#include <iostream>
#include <string>
#include <memory>
#include <signal.h>
#include <conio.h>

using namespace PacketAnalyzer;

// Global objects for signal handling
std::shared_ptr<PacketCapture> g_capture;
std::shared_ptr<Analyzer> g_analyzer;
bool g_running = true;

// Signal handler for Ctrl+C
void signalHandler(int signum) {
    std::cout << "\n\nInterrupt signal (" << signum << ") received.\n";
    g_running = false;

    if (g_capture) {
        g_capture->stopCapture();
    }

    if (g_analyzer) {
        g_analyzer->printStatistics();
    }

    std::cout << "\nExiting...\n";
    exit(signum);
}

// Packet callback function
void packetCallback(const struct pcap_pkthdr* header, const uint8_t* packet) {
    if (g_analyzer) {
        PacketInfo info = g_analyzer->analyzePacket(header, packet);
        g_analyzer->printPacketInfo(info);

        // Optionally print hex dump for first few bytes
        // g_analyzer->printHexDump(info.raw_data, info.raw_length, 64);

        // Check if user wants to stop (press 'q')
        if (_kbhit()) {
            char ch = _getch();
            if (ch == 'q' || ch == 'Q') {
                std::cout << "\n\nStopping capture...\n";
                g_running = false;
                if (g_capture) {
                    g_capture->stopCapture();
                }
            } else if (ch == 's' || ch == 'S') {
                std::cout << "\n";
                g_analyzer->printStatistics();
            }
        }
    }
}

void printMenu() {
    std::cout << "\n========================================" << std::endl;
    std::cout << "  Windows Packet Analyzer - C++" << std::endl;
    std::cout << "========================================" << std::endl;
    std::cout << "1. List all network interfaces" << std::endl;
    std::cout << "2. Start packet capture" << std::endl;
    std::cout << "3. Apply capture filter" << std::endl;
    std::cout << "4. View statistics" << std::endl;
    std::cout << "5. Reset statistics" << std::endl;
    std::cout << "0. Exit" << std::endl;
    std::cout << "========================================" << std::endl;
    std::cout << "Select option: ";
}

void printCaptureInstructions() {
    std::cout << "\n========================================" << std::endl;
    std::cout << "Capture is running..." << std::endl;
    std::cout << "Press 'Q' to stop capture" << std::endl;
    std::cout << "Press 'S' to view statistics" << std::endl;
    std::cout << "========================================\n" << std::endl;
}

int main(int argc, char* argv[]) {
    // Register signal handler
    signal(SIGINT, signalHandler);

    std::cout << "========================================" << std::endl;
    std::cout << "Windows Packet Analyzer" << std::endl;
    std::cout << "Network Interface Monitor & Packet Analyzer" << std::endl;
    std::cout << "========================================\n" << std::endl;

    // Create objects
    NetworkInterface netInterface;
    g_capture = std::make_shared<PacketCapture>();
    g_analyzer = std::make_shared<Analyzer>();

    std::string current_filter;
    bool interface_selected = false;

    while (g_running) {
        printMenu();

        int choice;
        std::cin >> choice;

        switch (choice) {
            case 1: {
                // List all interfaces
                std::cout << "\nScanning for network interfaces...\n";
                netInterface.getAllInterfaces();
                netInterface.displayInterfaces();

                std::cout << "Select interface number (or -1 to cancel): ";
                int index;
                std::cin >> index;

                if (index >= 0) {
                    if (netInterface.selectInterface(index)) {
                        std::cout << "\nSelected interface: "
                                  << netInterface.getSelectedInterfaceDescription() << std::endl;
                        interface_selected = true;
                    } else {
                        std::cout << "\nFailed to select interface!" << std::endl;
                    }
                }
                break;
            }

            case 2: {
                // Start packet capture
                if (!interface_selected) {
                    std::cout << "\nPlease select an interface first (option 1)!" << std::endl;
                    break;
                }

                std::string device_name = netInterface.getSelectedInterfaceName();
                std::cout << "\nOpening device: " << device_name << std::endl;

                if (!g_capture->openDevice(device_name, true)) {
                    std::cout << "Failed to open device!" << std::endl;
                    break;
                }

                // Apply filter if set
                if (!current_filter.empty()) {
                    std::cout << "Applying filter: " << current_filter << std::endl;
                    if (!g_capture->setFilter(current_filter)) {
                        std::cout << "Warning: Failed to apply filter" << std::endl;
                    }
                }

                std::cout << "\nHow many packets to capture? (0 for unlimited): ";
                int packet_count;
                std::cin >> packet_count;

                printCaptureInstructions();

                // Start capture (blocking)
                g_running = true;
                g_capture->startCapture(packetCallback, packet_count == 0 ? -1 : packet_count);

                std::cout << "\nCapture stopped." << std::endl;
                g_analyzer->printStatistics();

                g_capture->closeDevice();
                break;
            }

            case 3: {
                // Apply capture filter
                std::cout << "\nEnter BPF filter expression (e.g., 'tcp port 80', 'icmp', 'host 192.168.1.1')" << std::endl;
                std::cout << "Filter: ";
                std::cin.ignore();
                std::getline(std::cin, current_filter);

                if (current_filter.empty()) {
                    std::cout << "Filter cleared." << std::endl;
                } else {
                    std::cout << "Filter set to: " << current_filter << std::endl;
                    std::cout << "Filter will be applied on next capture." << std::endl;
                }
                break;
            }

            case 4: {
                // View statistics
                g_analyzer->printStatistics();
                break;
            }

            case 5: {
                // Reset statistics
                g_analyzer->resetStatistics();
                std::cout << "\nStatistics reset." << std::endl;
                break;
            }

            case 0: {
                // Exit
                std::cout << "\nExiting...\n";
                g_running = false;
                break;
            }

            default:
                std::cout << "\nInvalid option!" << std::endl;
                break;
        }
    }

    // Cleanup
    if (g_capture) {
        g_capture->closeDevice();
    }

    if (g_analyzer) {
        g_analyzer->printStatistics();
    }

    std::cout << "\nGoodbye!\n" << std::endl;

    return 0;
}
