import socket
import struct

# Function to parse Ethernet frames
def parse_ethernet_frame(data):
    dest_mac, src_mac, proto = struct.unpack('! 6s 6s H', data[:14])
    return format_mac_addr(dest_mac), format_mac_addr(src_mac), socket.htons(proto), data[14:]

# Function to format MAC address
def format_mac_addr(bytes_addr):
    bytes_str = map('{:02x}'.format, bytes_addr)
    return ':'.join(bytes_str).upper()

# Function to parse IPv4 packets
def parse_ipv4_packet(data):
    version_header_length = data[0]
    version = version_header_length >> 4
    header_length = (version_header_length & 15) * 4
    ttl, proto, src, target = struct.unpack('! 8x B B 2x 4s 4s', data[:20])
    return version, header_length, ttl, proto, socket.inet_ntoa(src), socket.inet_ntoa(target), data[header_length:]

# Function to parse TCP segments
def parse_tcp_segment(data):
    src_port, dest_port, sequence, acknowledgment, offset_reserved_flags = struct.unpack('! H H L L H', data[:14])
    offset = (offset_reserved_flags >> 12) * 4
    return src_port, dest_port, sequence, acknowledgment, data[offset:]

# Function to parse UDP segments
def parse_udp_segment(data):
    src_port, dest_port, length = struct.unpack('! H H 2x H', data[:8])
    return src_port, dest_port, length, data[8:]

# Function to sniff and analyze network packets
def sniff_packets(iface):
    # Create a raw socket and bind it to the network interface
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(3))
    sock.bind((iface, 0))

    try:
        while True:
            raw_data, addr = sock.recvfrom(65535)  # Maximum size of the packet
            dest_mac, src_mac, eth_proto, data = parse_ethernet_frame(raw_data)
            
            print(f'\nEthernet Frame:')
            print(f'Destination MAC: {dest_mac}, Source MAC: {src_mac}, Protocol: {eth_proto}')
            
            # Parse IPv4 packet
            if eth_proto == 0x0800:  # IPv4
                version, header_length, ttl, proto, src_ip, target_ip, data = parse_ipv4_packet(data)
                print(f'IPv4 Packet:')
                print(f'Source IP: {src_ip}, Destination IP: {target_ip}, Protocol: {proto}')
                
                # Parse TCP segment
                if proto == 6:  # TCP
                    src_port, dest_port, sequence, acknowledgment, data = parse_tcp_segment(data)
                    print(f'TCP Segment:')
                    print(f'Source Port: {src_port}, Destination Port: {dest_port}')
                
                # Parse UDP segment
                elif proto == 17:  # UDP
                    src_port, dest_port, length, data = parse_udp_segment(data)
                    print(f'UDP Segment:')
                    print(f'Source Port: {src_port}, Destination Port: {dest_port}')

    except KeyboardInterrupt:
        print("\nShutting down.")
        sock.close()

if __name__ == "__main__":
    sniff_packets('wlan0')  # Replace 'wlan0' with your network interface
