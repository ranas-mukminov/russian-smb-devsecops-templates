"""
Data models for router policy configuration.

This module defines the core data structures representing a vendor-agnostic
router policy that can be compiled into RouterOS and OpenWrt configurations.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Target:
    """Target platform configuration."""

    vendor: str  # routeros or openwrt
    version: Optional[str] = None  # e.g., v6, v7 for RouterOS


@dataclass
class Meta:
    """Policy metadata."""

    name: str
    description: Optional[str] = None
    target: Target = field(default_factory=lambda: Target(vendor="routeros"))


@dataclass
class WANConfig:
    """WAN (Wide Area Network) configuration."""

    type: str  # pppoe, dhcp, static
    interface: str  # Physical interface like ether1, eth0
    username: Optional[str] = None  # For PPPoE
    password_ref: Optional[str] = None  # Reference to secret
    ip: Optional[str] = None  # For static
    netmask: Optional[str] = None
    gateway: Optional[str] = None
    dns: List[str] = field(default_factory=list)
    mtu: Optional[int] = None


@dataclass
class DHCPConfig:
    """DHCP server configuration."""

    enabled: bool = False
    range: Optional[str] = None  # e.g., "192.168.10.100-192.168.10.200"
    lease_time: str = "24h"
    dns_servers: List[str] = field(default_factory=list)


@dataclass
class LANConfig:
    """LAN (Local Area Network) configuration."""

    name: str
    subnet: str  # CIDR notation, e.g., 192.168.10.0/24
    gateway: str  # Gateway IP
    vlan_id: Optional[int] = None
    interface: Optional[str] = None
    dhcp: Optional[DHCPConfig] = None
    isolated_from: List[str] = field(default_factory=list)


@dataclass
class SecurityConfig:
    """WiFi security configuration."""

    encryption: str  # none, wep, wpa-psk, wpa2-psk, wpa3-psk, wpa2-enterprise
    password_ref: Optional[str] = None
    radius_server: Optional[str] = None
    radius_secret_ref: Optional[str] = None


@dataclass
class WiFiConfig:
    """WiFi access point configuration."""

    name: str
    lan: str  # Associated LAN name
    ssid: str
    mode: str  # ap, sta, mesh
    channel: Optional[int] = None
    band: Optional[str] = None  # 2.4ghz, 5ghz, 6ghz
    hidden: bool = False
    guest: bool = False
    security: Optional[SecurityConfig] = None


@dataclass
class VPNPeer:
    """VPN peer configuration."""

    name: str
    public_key_ref: Optional[str] = None
    allowed_ips: List[str] = field(default_factory=list)


@dataclass
class VPNConfig:
    """VPN configuration."""

    type: str  # wireguard, openvpn, ipsec
    role: str  # server, client
    listen_port: Optional[int] = None
    interface: Optional[str] = None
    allowed_ips: List[str] = field(default_factory=list)
    endpoint: Optional[str] = None
    public_key_ref: Optional[str] = None
    private_key_ref: Optional[str] = None
    peers: List[VPNPeer] = field(default_factory=list)


@dataclass
class FirewallRule:
    """Firewall rule definition."""

    name: str
    action: str  # accept, drop, reject
    from_zones: List[str] = field(default_factory=list)
    to_zones: List[str] = field(default_factory=list)
    protocol: Optional[str] = None  # tcp, udp, icmp, all
    port: Optional[str] = None  # Port number or range
    state: List[str] = field(default_factory=list)
    log: bool = False
    comment: Optional[str] = None


@dataclass
class Firewall:
    """Firewall configuration."""

    default_policy: str = "drop"
    rules: List[FirewallRule] = field(default_factory=list)


@dataclass
class DNSConfig:
    """DNS configuration."""

    servers: List[str] = field(default_factory=list)
    domain: Optional[str] = None
    forwarders: List[str] = field(default_factory=list)


@dataclass
class PortForward:
    """Port forwarding rule."""

    name: Optional[str] = None
    protocol: str = "tcp"  # tcp, udp, both
    external_port: int = 0
    internal_ip: str = ""
    internal_port: int = 0


@dataclass
class NATConfig:
    """NAT configuration."""

    masquerade: bool = True
    port_forwards: List[PortForward] = field(default_factory=list)


@dataclass
class Policy:
    """
    Complete router policy.

    This represents the entire configuration policy that can be
    compiled into vendor-specific configurations.
    """

    meta: Meta
    wan: WANConfig
    lans: List[LANConfig] = field(default_factory=list)
    wifi: List[WiFiConfig] = field(default_factory=list)
    vpn: List[VPNConfig] = field(default_factory=list)
    firewall: Optional[Firewall] = None
    dns: Optional[DNSConfig] = None
    nat: Optional[NATConfig] = None
