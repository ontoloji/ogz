#include "PacketAnalyzer.h"
#include <iostream>
#include <iomanip>
#include <sstream>
#include <winsock2.h>

namespace PacketAnalyzer {

Analyzer::Analyzer()
    : total_packets_(0), ethernet_packets_(0), ipv4_packets_(0),
      ipv6_packets_(0), tcp_packets_(0), udp_packets_(0),
      icmp_packets_(0), arp_packets_(0), http_packets_(0),
      https_packets_(0), dns_packets_(0), other_packets_(0) {
}

Analyzer::~Analyzer() {
}

PacketInfo Analyzer::analyzePacket(const struct pcap_pkthdr* header, const uint8_t* packet) {
    PacketInfo info;

    if (!header || !packet) {
        return info;
    }

    total_packets_++;

    // Store timestamp and length
    info.timestamp = header->ts.tv_sec + (header->ts.tv_usec / 1000000.0);
    info.length = header->len;
    info.raw_data = packet;
    info.raw_length = header->caplen;

    // Analyze Ethernet frame
    if (analyzeEthernet(packet, header->caplen, info)) {
        ethernet_packets_++;

        // Generate description
        info.description = generateDescription(info);
    }

    return info;
}

bool Analyzer::analyzeEthernet(const uint8_t* packet, uint32_t length, PacketInfo& info) {
    if (length < sizeof(EthernetHeader)) {
        return false;
    }

    const EthernetHeader* eth = reinterpret_cast<const EthernetHeader*>(packet);

    info.src_mac = macToString(eth->src_mac);
    info.dest_mac = macToString(eth->dest_mac);
    info.ether_type = ntohs(eth->ether_type);
    info.type = PacketType::ETHERNET;

    const uint8_t* payload = packet + sizeof(EthernetHeader);
    uint32_t payload_length = length - sizeof(EthernetHeader);

    // Determine next layer protocol
    switch (info.ether_type) {
        case ETHER_TYPE_IPv4:
            analyzeIPv4(payload, payload_length, info);
            break;
        case ETHER_TYPE_IPv6:
            analyzeIPv6(payload, payload_length, info);
            break;
        case ETHER_TYPE_ARP:
            analyzeARP(payload, payload_length, info);
            break;
        default:
            other_packets_++;
            break;
    }

    return true;
}

bool Analyzer::analyzeIPv4(const uint8_t* packet, uint32_t length, PacketInfo& info) {
    if (length < sizeof(IPv4Header)) {
        return false;
    }

    const IPv4Header* ip = reinterpret_cast<const IPv4Header*>(packet);

    info.ip_version = 4;
    info.src_ip = ipv4ToString(ip->src_ip);
    info.dest_ip = ipv4ToString(ip->dest_ip);
    info.protocol = ip->protocol;
    info.ttl = ip->ttl;
    info.ip_length = ntohs(ip->total_length);
    info.type = PacketType::IPv4;

    ipv4_packets_++;

    uint8_t ihl = (ip->version_ihl & 0x0F) * 4;
    const uint8_t* payload = packet + ihl;
    uint32_t payload_length = length - ihl;

    // Analyze transport layer
    switch (info.protocol) {
        case PROTO_TCP:
            analyzeTCP(payload, payload_length, info);
            break;
        case PROTO_UDP:
            analyzeUDP(payload, payload_length, info);
            break;
        case PROTO_ICMP:
            analyzeICMP(payload, payload_length, info);
            break;
        default:
            info.protocol_name = "Other (" + std::to_string(info.protocol) + ")";
            other_packets_++;
            break;
    }

    return true;
}

bool Analyzer::analyzeIPv6(const uint8_t* packet, uint32_t length, PacketInfo& info) {
    if (length < sizeof(IPv6Header)) {
        return false;
    }

    const IPv6Header* ip = reinterpret_cast<const IPv6Header*>(packet);

    info.ip_version = 6;
    info.src_ip = ipv6ToString(ip->src_ip);
    info.dest_ip = ipv6ToString(ip->dest_ip);
    info.protocol = ip->next_header;
    info.ttl = ip->hop_limit;
    info.ip_length = ntohs(ip->payload_length);
    info.type = PacketType::IPv6;

    ipv6_packets_++;

    const uint8_t* payload = packet + sizeof(IPv6Header);
    uint32_t payload_length = length - sizeof(IPv6Header);

    // Analyze transport layer
    switch (info.protocol) {
        case PROTO_TCP:
            analyzeTCP(payload, payload_length, info);
            break;
        case PROTO_UDP:
            analyzeUDP(payload, payload_length, info);
            break;
        case PROTO_ICMPv6:
            analyzeICMP(payload, payload_length, info);
            break;
        default:
            info.protocol_name = "Other (" + std::to_string(info.protocol) + ")";
            other_packets_++;
            break;
    }

    return true;
}

bool Analyzer::analyzeTCP(const uint8_t* packet, uint32_t length, PacketInfo& info) {
    if (length < sizeof(TCPHeader)) {
        return false;
    }

    const TCPHeader* tcp = reinterpret_cast<const TCPHeader*>(packet);

    info.src_port = ntohs(tcp->src_port);
    info.dest_port = ntohs(tcp->dest_port);
    info.tcp_seq = ntohl(tcp->seq_number);
    info.tcp_ack = ntohl(tcp->ack_number);
    info.tcp_flags = tcp->flags;
    info.type = PacketType::TCP;
    info.protocol_name = "TCP";

    tcp_packets_++;

    // Detect application protocol
    detectApplicationProtocol(info);

    return true;
}

bool Analyzer::analyzeUDP(const uint8_t* packet, uint32_t length, PacketInfo& info) {
    if (length < sizeof(UDPHeader)) {
        return false;
    }

    const UDPHeader* udp = reinterpret_cast<const UDPHeader*>(packet);

    info.src_port = ntohs(udp->src_port);
    info.dest_port = ntohs(udp->dest_port);
    info.type = PacketType::UDP;
    info.protocol_name = "UDP";

    udp_packets_++;

    // Detect application protocol
    detectApplicationProtocol(info);

    return true;
}

bool Analyzer::analyzeICMP(const uint8_t* packet, uint32_t length, PacketInfo& info) {
    if (length < sizeof(ICMPHeader)) {
        return false;
    }

    const ICMPHeader* icmp = reinterpret_cast<const ICMPHeader*>(packet);

    info.type = PacketType::ICMP;
    info.protocol_name = "ICMP";

    icmp_packets_++;

    // ICMP type descriptions
    std::string icmp_type;
    switch (icmp->type) {
        case 0: icmp_type = "Echo Reply"; break;
        case 3: icmp_type = "Destination Unreachable"; break;
        case 8: icmp_type = "Echo Request"; break;
        case 11: icmp_type = "Time Exceeded"; break;
        default: icmp_type = "Type " + std::to_string(icmp->type); break;
    }

    info.protocol_name = "ICMP (" + icmp_type + ")";

    return true;
}

bool Analyzer::analyzeARP(const uint8_t* packet, uint32_t length, PacketInfo& info) {
    if (length < sizeof(ARPHeader)) {
        return false;
    }

    const ARPHeader* arp = reinterpret_cast<const ARPHeader*>(packet);

    info.type = PacketType::ARP;
    info.protocol_name = "ARP";

    arp_packets_++;

    uint16_t operation = ntohs(arp->operation);
    if (operation == 1) {
        info.protocol_name = "ARP Request";
    } else if (operation == 2) {
        info.protocol_name = "ARP Reply";
    }

    info.src_ip = ipv4ToString(arp->sender_proto_addr);
    info.dest_ip = ipv4ToString(arp->target_proto_addr);

    return true;
}

void Analyzer::detectApplicationProtocol(PacketInfo& info) {
    if (info.src_port == PORT_HTTP || info.dest_port == PORT_HTTP) {
        info.type = PacketType::HTTP;
        info.protocol_name = "HTTP";
        http_packets_++;
    } else if (info.src_port == PORT_HTTPS || info.dest_port == PORT_HTTPS) {
        info.type = PacketType::HTTPS;
        info.protocol_name = "HTTPS";
        https_packets_++;
    } else if (info.src_port == PORT_DNS || info.dest_port == PORT_DNS) {
        info.type = PacketType::DNS;
        info.protocol_name = "DNS";
        dns_packets_++;
    }
}

std::string Analyzer::getTCPFlagsString(uint8_t flags) {
    std::string result;
    if (flags & 0x01) result += "FIN ";
    if (flags & 0x02) result += "SYN ";
    if (flags & 0x04) result += "RST ";
    if (flags & 0x08) result += "PSH ";
    if (flags & 0x10) result += "ACK ";
    if (flags & 0x20) result += "URG ";
    if (result.empty()) result = "None";
    else result.pop_back(); // Remove trailing space
    return result;
}

std::string Analyzer::generateDescription(const PacketInfo& info) {
    std::ostringstream desc;

    switch (info.type) {
        case PacketType::TCP:
        case PacketType::UDP:
        case PacketType::HTTP:
        case PacketType::HTTPS:
        case PacketType::DNS:
            desc << info.protocol_name << " packet from "
                 << info.src_ip << ":" << info.src_port
                 << " to " << info.dest_ip << ":" << info.dest_port;
            if (info.type == PacketType::TCP) {
                desc << " [" << getTCPFlagsString(info.tcp_flags) << "]";
            }
            break;

        case PacketType::ICMP:
            desc << info.protocol_name << " from "
                 << info.src_ip << " to " << info.dest_ip;
            break;

        case PacketType::ARP:
            desc << info.protocol_name << ": "
                 << info.src_ip << " -> " << info.dest_ip;
            break;

        case PacketType::IPv4:
        case PacketType::IPv6:
            desc << "IP packet from " << info.src_ip
                 << " to " << info.dest_ip;
            break;

        default:
            desc << "Ethernet frame from " << info.src_mac
                 << " to " << info.dest_mac;
            break;
    }

    return desc.str();
}

void Analyzer::printPacketInfo(const PacketInfo& info) {
    std::cout << "\n----------------------------------------" << std::endl;
    std::cout << "Packet #" << total_packets_ << std::endl;
    std::cout << "Time: " << std::fixed << std::setprecision(6) << info.timestamp << std::endl;
    std::cout << "Length: " << info.length << " bytes" << std::endl;
    std::cout << "Type: " << packetTypeToString(info.type) << std::endl;

    std::cout << "\nEthernet Layer:" << std::endl;
    std::cout << "  Source MAC: " << info.src_mac << std::endl;
    std::cout << "  Dest MAC: " << info.dest_mac << std::endl;
    std::cout << "  Type: 0x" << std::hex << info.ether_type << std::dec << std::endl;

    if (info.ip_version > 0) {
        std::cout << "\nIP Layer (v" << static_cast<int>(info.ip_version) << "):" << std::endl;
        std::cout << "  Source IP: " << info.src_ip << std::endl;
        std::cout << "  Dest IP: " << info.dest_ip << std::endl;
        std::cout << "  Protocol: " << info.protocol_name << " (" << static_cast<int>(info.protocol) << ")" << std::endl;
        std::cout << "  TTL: " << static_cast<int>(info.ttl) << std::endl;
    }

    if (info.src_port > 0 || info.dest_port > 0) {
        std::cout << "\nTransport Layer:" << std::endl;
        std::cout << "  Source Port: " << info.src_port << std::endl;
        std::cout << "  Dest Port: " << info.dest_port << std::endl;

        if (info.type == PacketType::TCP) {
            std::cout << "  Seq: " << info.tcp_seq << std::endl;
            std::cout << "  Ack: " << info.tcp_ack << std::endl;
            std::cout << "  Flags: " << getTCPFlagsString(info.tcp_flags) << std::endl;
        }
    }

    std::cout << "\nDescription: " << info.description << std::endl;
    std::cout << "----------------------------------------" << std::endl;
}

void Analyzer::printHexDump(const uint8_t* data, uint32_t length, uint32_t max_bytes) {
    if (!data || length == 0) return;

    uint32_t bytes_to_print = (length < max_bytes) ? length : max_bytes;

    std::cout << "\nHex Dump (first " << bytes_to_print << " bytes):" << std::endl;

    for (uint32_t i = 0; i < bytes_to_print; i += 16) {
        std::cout << std::setw(4) << std::setfill('0') << std::hex << i << "  ";

        // Print hex
        for (uint32_t j = 0; j < 16; ++j) {
            if (i + j < bytes_to_print) {
                std::cout << std::setw(2) << std::setfill('0') << std::hex
                         << static_cast<int>(data[i + j]) << " ";
            } else {
                std::cout << "   ";
            }
            if (j == 7) std::cout << " ";
        }

        std::cout << " ";

        // Print ASCII
        for (uint32_t j = 0; j < 16 && i + j < bytes_to_print; ++j) {
            char c = data[i + j];
            std::cout << (isprint(c) ? c : '.');
        }

        std::cout << std::endl;
    }

    std::cout << std::dec;

    if (length > max_bytes) {
        std::cout << "... (" << (length - max_bytes) << " more bytes)" << std::endl;
    }
}

void Analyzer::printStatistics() {
    std::cout << "\n========================================" << std::endl;
    std::cout << "Packet Capture Statistics" << std::endl;
    std::cout << "========================================" << std::endl;
    std::cout << "Total Packets: " << total_packets_ << std::endl;
    std::cout << "\nBy Protocol:" << std::endl;
    std::cout << "  Ethernet: " << ethernet_packets_ << std::endl;
    std::cout << "  ARP: " << arp_packets_ << std::endl;
    std::cout << "  IPv4: " << ipv4_packets_ << std::endl;
    std::cout << "  IPv6: " << ipv6_packets_ << std::endl;
    std::cout << "  TCP: " << tcp_packets_ << std::endl;
    std::cout << "  UDP: " << udp_packets_ << std::endl;
    std::cout << "  ICMP: " << icmp_packets_ << std::endl;
    std::cout << "\nBy Application:" << std::endl;
    std::cout << "  HTTP: " << http_packets_ << std::endl;
    std::cout << "  HTTPS: " << https_packets_ << std::endl;
    std::cout << "  DNS: " << dns_packets_ << std::endl;
    std::cout << "  Other: " << other_packets_ << std::endl;
    std::cout << "========================================\n" << std::endl;
}

void Analyzer::resetStatistics() {
    total_packets_ = 0;
    ethernet_packets_ = 0;
    ipv4_packets_ = 0;
    ipv6_packets_ = 0;
    tcp_packets_ = 0;
    udp_packets_ = 0;
    icmp_packets_ = 0;
    arp_packets_ = 0;
    http_packets_ = 0;
    https_packets_ = 0;
    dns_packets_ = 0;
    other_packets_ = 0;
}

} // namespace PacketAnalyzer
