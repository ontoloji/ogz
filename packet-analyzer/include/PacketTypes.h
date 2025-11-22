#ifndef PACKET_TYPES_H
#define PACKET_TYPES_H

#include <string>
#include <cstdint>

namespace PacketAnalyzer {

// Ethernet frame structure
struct EthernetHeader {
    uint8_t dest_mac[6];
    uint8_t src_mac[6];
    uint16_t ether_type;
};

// IPv4 header structure
struct IPv4Header {
    uint8_t version_ihl;
    uint8_t tos;
    uint16_t total_length;
    uint16_t identification;
    uint16_t flags_fragment;
    uint8_t ttl;
    uint8_t protocol;
    uint16_t checksum;
    uint32_t src_ip;
    uint32_t dest_ip;
};

// IPv6 header structure
struct IPv6Header {
    uint32_t version_class_flow;
    uint16_t payload_length;
    uint8_t next_header;
    uint8_t hop_limit;
    uint8_t src_ip[16];
    uint8_t dest_ip[16];
};

// TCP header structure
struct TCPHeader {
    uint16_t src_port;
    uint16_t dest_port;
    uint32_t seq_number;
    uint32_t ack_number;
    uint8_t data_offset;
    uint8_t flags;
    uint16_t window;
    uint16_t checksum;
    uint16_t urgent_pointer;
};

// UDP header structure
struct UDPHeader {
    uint16_t src_port;
    uint16_t dest_port;
    uint16_t length;
    uint16_t checksum;
};

// ICMP header structure
struct ICMPHeader {
    uint8_t type;
    uint8_t code;
    uint16_t checksum;
    uint32_t rest;
};

// ARP header structure
struct ARPHeader {
    uint16_t hw_type;
    uint16_t proto_type;
    uint8_t hw_addr_len;
    uint8_t proto_addr_len;
    uint16_t operation;
    uint8_t sender_hw_addr[6];
    uint32_t sender_proto_addr;
    uint8_t target_hw_addr[6];
    uint32_t target_proto_addr;
};

// Packet type enumeration
enum class PacketType {
    ETHERNET,
    ARP,
    IPv4,
    IPv6,
    TCP,
    UDP,
    ICMP,
    DNS,
    HTTP,
    HTTPS,
    UNKNOWN
};

// Protocol numbers
const uint8_t PROTO_ICMP = 1;
const uint8_t PROTO_TCP = 6;
const uint8_t PROTO_UDP = 17;
const uint8_t PROTO_ICMPv6 = 58;

// Ethernet types
const uint16_t ETHER_TYPE_IPv4 = 0x0800;
const uint16_t ETHER_TYPE_ARP = 0x0806;
const uint16_t ETHER_TYPE_IPv6 = 0x86DD;

// Well-known ports
const uint16_t PORT_HTTP = 80;
const uint16_t PORT_HTTPS = 443;
const uint16_t PORT_DNS = 53;

// Helper function to convert packet type to string
std::string packetTypeToString(PacketType type);

// Helper function to convert MAC address to string
std::string macToString(const uint8_t* mac);

// Helper function to convert IPv4 address to string
std::string ipv4ToString(uint32_t ip);

// Helper function to convert IPv6 address to string
std::string ipv6ToString(const uint8_t* ip);

} // namespace PacketAnalyzer

#endif // PACKET_TYPES_H
