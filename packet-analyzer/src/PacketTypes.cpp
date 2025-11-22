#include "PacketTypes.h"
#include <sstream>
#include <iomanip>

namespace PacketAnalyzer {

std::string packetTypeToString(PacketType type) {
    switch (type) {
        case PacketType::ETHERNET: return "ETHERNET";
        case PacketType::ARP: return "ARP";
        case PacketType::IPv4: return "IPv4";
        case PacketType::IPv6: return "IPv6";
        case PacketType::TCP: return "TCP";
        case PacketType::UDP: return "UDP";
        case PacketType::ICMP: return "ICMP";
        case PacketType::DNS: return "DNS";
        case PacketType::HTTP: return "HTTP";
        case PacketType::HTTPS: return "HTTPS";
        default: return "UNKNOWN";
    }
}

std::string macToString(const uint8_t* mac) {
    std::ostringstream oss;
    oss << std::hex << std::setfill('0');
    for (int i = 0; i < 6; ++i) {
        if (i > 0) oss << ":";
        oss << std::setw(2) << static_cast<int>(mac[i]);
    }
    return oss.str();
}

std::string ipv4ToString(uint32_t ip) {
    std::ostringstream oss;
    oss << ((ip >> 0) & 0xFF) << "."
        << ((ip >> 8) & 0xFF) << "."
        << ((ip >> 16) & 0xFF) << "."
        << ((ip >> 24) & 0xFF);
    return oss.str();
}

std::string ipv6ToString(const uint8_t* ip) {
    std::ostringstream oss;
    oss << std::hex << std::setfill('0');
    for (int i = 0; i < 16; i += 2) {
        if (i > 0) oss << ":";
        oss << std::setw(2) << static_cast<int>(ip[i])
            << std::setw(2) << static_cast<int>(ip[i + 1]);
    }
    return oss.str();
}

} // namespace PacketAnalyzer
