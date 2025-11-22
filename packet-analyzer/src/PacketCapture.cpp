#include "PacketCapture.h"
#include <iostream>

namespace PacketAnalyzer {

PacketCapture::PacketCapture()
    : pcap_handle_(nullptr), is_capturing_(false) {
    error_buffer_[0] = '\0';
}

PacketCapture::~PacketCapture() {
    stopCapture();
    closeDevice();
}

bool PacketCapture::openDevice(const std::string& device_name, bool promiscuous) {
    closeDevice();

    // Open device for capturing
    // Parameters: device name, snapshot length, promiscuous mode, timeout (ms), error buffer
    pcap_handle_ = pcap_open_live(
        device_name.c_str(),
        65536,  // snapshot length
        promiscuous ? 1 : 0,
        1000,   // read timeout in milliseconds
        error_buffer_
    );

    if (pcap_handle_ == nullptr) {
        std::cerr << "Error opening device " << device_name << ": "
                  << error_buffer_ << std::endl;
        return false;
    }

    std::cout << "Successfully opened device: " << device_name << std::endl;
    return true;
}

void PacketCapture::closeDevice() {
    if (pcap_handle_) {
        pcap_close(pcap_handle_);
        pcap_handle_ = nullptr;
    }
}

bool PacketCapture::setFilter(const std::string& filter_exp) {
    if (!pcap_handle_) {
        std::cerr << "Device not opened" << std::endl;
        return false;
    }

    struct bpf_program fp;
    bpf_u_int32 net = 0;

    if (pcap_compile(pcap_handle_, &fp, filter_exp.c_str(), 0, net) == -1) {
        std::cerr << "Error compiling filter: " << pcap_geterr(pcap_handle_) << std::endl;
        return false;
    }

    if (pcap_setfilter(pcap_handle_, &fp) == -1) {
        std::cerr << "Error setting filter: " << pcap_geterr(pcap_handle_) << std::endl;
        pcap_freecode(&fp);
        return false;
    }

    pcap_freecode(&fp);
    std::cout << "Filter applied: " << filter_exp << std::endl;
    return true;
}

void PacketCapture::packetHandler(u_char* user_data, const struct pcap_pkthdr* header, const u_char* packet) {
    PacketCapture* capture = reinterpret_cast<PacketCapture*>(user_data);
    if (capture && capture->callback_) {
        capture->callback_(header, packet);
    }
}

void PacketCapture::startCapture(PacketCallback callback, int packet_count) {
    if (!pcap_handle_) {
        std::cerr << "Device not opened" << std::endl;
        return;
    }

    callback_ = callback;
    is_capturing_ = true;

    std::cout << "Starting packet capture..." << std::endl;

    // Start capturing packets
    pcap_loop(pcap_handle_, packet_count, packetHandler, reinterpret_cast<u_char*>(this));

    is_capturing_ = false;
}

void PacketCapture::captureLoop() {
    if (pcap_handle_) {
        pcap_loop(pcap_handle_, -1, packetHandler, reinterpret_cast<u_char*>(this));
    }
    is_capturing_ = false;
}

bool PacketCapture::startCaptureAsync(PacketCallback callback) {
    if (!pcap_handle_) {
        std::cerr << "Device not opened" << std::endl;
        return false;
    }

    if (is_capturing_) {
        std::cerr << "Capture already in progress" << std::endl;
        return false;
    }

    callback_ = callback;
    is_capturing_ = true;

    std::cout << "Starting async packet capture..." << std::endl;

    capture_thread_ = std::thread(&PacketCapture::captureLoop, this);

    return true;
}

void PacketCapture::stopCapture() {
    if (is_capturing_ && pcap_handle_) {
        std::cout << "Stopping packet capture..." << std::endl;
        pcap_breakloop(pcap_handle_);
        is_capturing_ = false;

        if (capture_thread_.joinable()) {
            capture_thread_.join();
        }
    }
}

bool PacketCapture::isCapturing() const {
    return is_capturing_;
}

bool PacketCapture::getStatistics(struct pcap_stat& stats) {
    if (!pcap_handle_) {
        return false;
    }

    if (pcap_stats(pcap_handle_, &stats) == -1) {
        std::cerr << "Error getting statistics: " << pcap_geterr(pcap_handle_) << std::endl;
        return false;
    }

    return true;
}

std::string PacketCapture::getLastError() const {
    return std::string(error_buffer_);
}

} // namespace PacketAnalyzer
