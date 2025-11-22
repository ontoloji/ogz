#ifndef PACKET_ANALYZER_H
#define PACKET_ANALYZER_H

#include "PacketTypes.h"
#include <string>
#include <cstdint>
#include <memory>

namespace PacketAnalyzer {

// Detailed packet information
struct PacketInfo {
    // Timestamp
    double timestamp;

    // Packet size
    uint32_t length;

    // Ethernet info
    std::string src_mac;
    std::string dest_mac;
    uint16_t ether_type;

    // IP info
    std::string src_ip;
    std::string dest_ip;
    uint8_t ip_version;
    uint8_t protocol;
    uint16_t ip_length;
    uint8_t ttl;

    // Transport layer info
    uint16_t src_port;
    uint16_t dest_port;

    // Packet type
    PacketType type;

    // Additional info
    std::string protocol_name;
    std::string description;

    // TCP specific
    uint32_t tcp_seq;
    uint32_t tcp_ack;
    uint8_t tcp_flags;

    // Raw data pointer
    const uint8_t* raw_data;
    uint32_t raw_length;

    PacketInfo() : timestamp(0), length(0), ether_type(0), ip_version(0),
                   protocol(0), ip_length(0), ttl(0), src_port(0), dest_port(0),
                   type(PacketType::UNKNOWN), tcp_seq(0), tcp_ack(0),
                   tcp_flags(0), raw_data(nullptr), raw_length(0) {}
};

class Analyzer {
public:
    Analyzer();
    ~Analyzer();

    // Analyze packet and return detailed information
    PacketInfo analyzePacket(const struct pcap_pkthdr* header, const uint8_t* packet);

    // Print packet information to console
    void printPacketInfo(const PacketInfo& info);

    // Print packet in hexdump format
    void printHexDump(const uint8_t* data, uint32_t length, uint32_t max_bytes = 64);

    // Get packet statistics
    void printStatistics();

    // Reset statistics
    void resetStatistics();

private:
    // Statistics counters
    uint64_t total_packets_;
    uint64_t ethernet_packets_;
    uint64_t ipv4_packets_;
    uint64_t ipv6_packets_;
    uint64_t tcp_packets_;
    uint64_t udp_packets_;
    uint64_t icmp_packets_;
    uint64_t arp_packets_;
    uint64_t http_packets_;
    uint64_t https_packets_;
    uint64_t dns_packets_;
    uint64_t other_packets_;

    // Analyze Ethernet frame
    bool analyzeEthernet(const uint8_t* packet, uint32_t length, PacketInfo& info);

    // Analyze IPv4 packet
    bool analyzeIPv4(const uint8_t* packet, uint32_t length, PacketInfo& info);

    // Analyze IPv6 packet
    bool analyzeIPv6(const uint8_t* packet, uint32_t length, PacketInfo& info);

    // Analyze TCP segment
    bool analyzeTCP(const uint8_t* packet, uint32_t length, PacketInfo& info);

    // Analyze UDP datagram
    bool analyzeUDP(const uint8_t* packet, uint32_t length, PacketInfo& info);

    // Analyze ICMP packet
    bool analyzeICMP(const uint8_t* packet, uint32_t length, PacketInfo& info);

    // Analyze ARP packet
    bool analyzeARP(const uint8_t* packet, uint32_t length, PacketInfo& info);

    // Detect application layer protocol
    void detectApplicationProtocol(PacketInfo& info);

    // Generate packet description
    std::string generateDescription(const PacketInfo& info);

    // Helper to get TCP flags string
    std::string getTCPFlagsString(uint8_t flags);
};

} // namespace PacketAnalyzer

#endif // PACKET_ANALYZER_H
