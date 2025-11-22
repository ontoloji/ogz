#ifndef PACKET_CAPTURE_H
#define PACKET_CAPTURE_H

#include <string>
#include <functional>
#include <pcap.h>
#include <atomic>
#include <thread>

namespace PacketAnalyzer {

// Callback function type for packet processing
using PacketCallback = std::function<void(const struct pcap_pkthdr*, const uint8_t*)>;

class PacketCapture {
public:
    PacketCapture();
    ~PacketCapture();

    // Open device for packet capture
    bool openDevice(const std::string& device_name, bool promiscuous = true);

    // Close capture device
    void closeDevice();

    // Start capturing packets (blocking)
    void startCapture(PacketCallback callback, int packet_count = -1);

    // Start capturing packets in a separate thread (non-blocking)
    bool startCaptureAsync(PacketCallback callback);

    // Stop async capture
    void stopCapture();

    // Check if capture is running
    bool isCapturing() const;

    // Set capture filter (BPF filter)
    bool setFilter(const std::string& filter_exp);

    // Get statistics
    bool getStatistics(struct pcap_stat& stats);

    // Get last error message
    std::string getLastError() const;

private:
    pcap_t* pcap_handle_;
    std::atomic<bool> is_capturing_;
    std::thread capture_thread_;
    char error_buffer_[PCAP_ERRBUF_SIZE];
    PacketCallback callback_;

    // Static callback for pcap_loop
    static void packetHandler(u_char* user_data, const struct pcap_pkthdr* header, const u_char* packet);

    // Capture loop for async capture
    void captureLoop();
};

} // namespace PacketAnalyzer

#endif // PACKET_CAPTURE_H
