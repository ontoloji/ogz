#ifndef NETWORK_INTERFACE_H
#define NETWORK_INTERFACE_H

#include <string>
#include <vector>
#include <pcap.h>

namespace PacketAnalyzer {

// Structure to hold network interface information
struct InterfaceInfo {
    std::string name;
    std::string description;
    std::string address;
    std::string netmask;
    bool is_loopback;

    InterfaceInfo() : is_loopback(false) {}
};

class NetworkInterface {
public:
    NetworkInterface();
    ~NetworkInterface();

    // Get all available network interfaces
    std::vector<InterfaceInfo> getAllInterfaces();

    // Display all interfaces to console
    void displayInterfaces();

    // Select interface by index
    bool selectInterface(int index);

    // Select interface by name
    bool selectInterface(const std::string& name);

    // Get selected interface name
    std::string getSelectedInterfaceName() const;

    // Get selected interface description
    std::string getSelectedInterfaceDescription() const;

    // Check if interface is selected
    bool isInterfaceSelected() const;

private:
    std::vector<InterfaceInfo> interfaces_;
    int selected_index_;
    pcap_if_t* all_devs_;

    // Free device list
    void freeDevices();

    // Helper to get address string
    std::string getAddressString(struct sockaddr* addr);
};

} // namespace PacketAnalyzer

#endif // NETWORK_INTERFACE_H
