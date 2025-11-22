#include "NetworkInterface.h"
#include <iostream>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <iphlpapi.h>

namespace PacketAnalyzer {

NetworkInterface::NetworkInterface()
    : selected_index_(-1), all_devs_(nullptr) {
}

NetworkInterface::~NetworkInterface() {
    freeDevices();
}

void NetworkInterface::freeDevices() {
    if (all_devs_) {
        pcap_freealldevs(all_devs_);
        all_devs_ = nullptr;
    }
}

std::string NetworkInterface::getAddressString(struct sockaddr* addr) {
    if (!addr) return "N/A";

    char ip_str[INET6_ADDRSTRLEN];

    if (addr->sa_family == AF_INET) {
        struct sockaddr_in* addr_in = (struct sockaddr_in*)addr;
        inet_ntop(AF_INET, &(addr_in->sin_addr), ip_str, INET_ADDRSTRLEN);
        return std::string(ip_str);
    } else if (addr->sa_family == AF_INET6) {
        struct sockaddr_in6* addr_in6 = (struct sockaddr_in6*)addr;
        inet_ntop(AF_INET6, &(addr_in6->sin6_addr), ip_str, INET6_ADDRSTRLEN);
        return std::string(ip_str);
    }

    return "Unknown";
}

std::vector<InterfaceInfo> NetworkInterface::getAllInterfaces() {
    interfaces_.clear();
    freeDevices();

    char errbuf[PCAP_ERRBUF_SIZE];

    if (pcap_findalldevs(&all_devs_, errbuf) == -1) {
        std::cerr << "Error finding devices: " << errbuf << std::endl;
        return interfaces_;
    }

    int index = 0;
    for (pcap_if_t* dev = all_devs_; dev != nullptr; dev = dev->next) {
        InterfaceInfo info;
        info.name = dev->name ? dev->name : "";
        info.description = dev->description ? dev->description : "No description";
        info.is_loopback = (dev->flags & PCAP_IF_LOOPBACK) != 0;

        if (dev->addresses) {
            pcap_addr_t* addr = dev->addresses;
            info.address = getAddressString(addr->addr);
            if (addr->netmask) {
                info.netmask = getAddressString(addr->netmask);
            }
        }

        interfaces_.push_back(info);
        index++;
    }

    return interfaces_;
}

void NetworkInterface::displayInterfaces() {
    if (interfaces_.empty()) {
        getAllInterfaces();
    }

    std::cout << "\n========================================" << std::endl;
    std::cout << "Available Network Interfaces:" << std::endl;
    std::cout << "========================================" << std::endl;

    for (size_t i = 0; i < interfaces_.size(); ++i) {
        std::cout << "\n[" << i << "] " << interfaces_[i].name << std::endl;
        std::cout << "    Description: " << interfaces_[i].description << std::endl;
        std::cout << "    Address: " << interfaces_[i].address << std::endl;
        if (!interfaces_[i].netmask.empty()) {
            std::cout << "    Netmask: " << interfaces_[i].netmask << std::endl;
        }
        std::cout << "    Loopback: " << (interfaces_[i].is_loopback ? "Yes" : "No") << std::endl;
    }
    std::cout << "\n========================================\n" << std::endl;
}

bool NetworkInterface::selectInterface(int index) {
    if (index < 0 || index >= static_cast<int>(interfaces_.size())) {
        std::cerr << "Invalid interface index: " << index << std::endl;
        return false;
    }

    selected_index_ = index;
    return true;
}

bool NetworkInterface::selectInterface(const std::string& name) {
    for (size_t i = 0; i < interfaces_.size(); ++i) {
        if (interfaces_[i].name == name) {
            selected_index_ = static_cast<int>(i);
            return true;
        }
    }
    std::cerr << "Interface not found: " << name << std::endl;
    return false;
}

std::string NetworkInterface::getSelectedInterfaceName() const {
    if (selected_index_ < 0 || selected_index_ >= static_cast<int>(interfaces_.size())) {
        return "";
    }
    return interfaces_[selected_index_].name;
}

std::string NetworkInterface::getSelectedInterfaceDescription() const {
    if (selected_index_ < 0 || selected_index_ >= static_cast<int>(interfaces_.size())) {
        return "";
    }
    return interfaces_[selected_index_].description;
}

bool NetworkInterface::isInterfaceSelected() const {
    return selected_index_ >= 0 && selected_index_ < static_cast<int>(interfaces_.size());
}

} // namespace PacketAnalyzer
