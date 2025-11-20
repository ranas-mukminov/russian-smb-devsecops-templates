"""
Policy semantic validator.

Performs semantic validation beyond JSON schema validation,
such as checking for subnet overlaps, referential integrity, etc.
"""

import ipaddress
from typing import List, Set

from router_policy_to_config.model import Policy


class ValidationError(Exception):
    """Exception raised when semantic validation fails."""

    pass


class PolicyValidator:
    """Semantic validator for router policies."""

    def __init__(self, policy: Policy):
        """
        Initialize validator with a policy.

        Args:
            policy: Policy instance to validate
        """
        self.policy = policy
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def _check_subnet_overlaps(self) -> None:
        """Check for overlapping subnets in LANs."""
        networks = []
        for lan in self.policy.lans:
            try:
                network = ipaddress.ip_network(lan.subnet, strict=False)
                networks.append((lan.name, network))
            except ValueError as e:
                self.errors.append(f"Invalid subnet for LAN '{lan.name}': {e}")

        # Check for overlaps
        for i, (name1, net1) in enumerate(networks):
            for name2, net2 in networks[i + 1 :]:
                if net1.overlaps(net2):
                    self.errors.append(f"Subnets overlap: '{name1}' ({net1}) and '{name2}' ({net2})")

    def _check_gateway_in_subnet(self) -> None:
        """Verify gateway IPs are within their respective subnets."""
        for lan in self.policy.lans:
            try:
                network = ipaddress.ip_network(lan.subnet, strict=False)
                gateway = ipaddress.ip_address(lan.gateway)

                if gateway not in network:
                    self.errors.append(f"Gateway {lan.gateway} is not in subnet {lan.subnet} for LAN '{lan.name}'")
            except ValueError as e:
                self.errors.append(f"Invalid IP for LAN '{lan.name}': {e}")

    def _check_dhcp_ranges(self) -> None:
        """Validate DHCP ranges are within LAN subnets."""
        for lan in self.policy.lans:
            if lan.dhcp and lan.dhcp.enabled and lan.dhcp.range:
                try:
                    network = ipaddress.ip_network(lan.subnet, strict=False)
                    start_str, end_str = lan.dhcp.range.split("-")
                    start_ip = ipaddress.ip_address(start_str.strip())
                    end_ip = ipaddress.ip_address(end_str.strip())

                    if start_ip not in network:
                        self.errors.append(
                            f"DHCP range start {start_ip} is not in subnet {lan.subnet} for LAN '{lan.name}'"
                        )

                    if end_ip not in network:
                        self.errors.append(
                            f"DHCP range end {end_ip} is not in subnet {lan.subnet} for LAN '{lan.name}'"
                        )

                    if start_ip >= end_ip:
                        self.errors.append(f"Invalid DHCP range for LAN '{lan.name}': start >= end")

                except (ValueError, AttributeError) as e:
                    self.errors.append(f"Invalid DHCP range for LAN '{lan.name}': {e}")

    def _check_wan_required_fields(self) -> None:
        """Check WAN type has required fields."""
        wan = self.policy.wan

        if wan.type == "pppoe":
            if not wan.username:
                self.errors.append("PPPoE WAN requires username")
            if not wan.password_ref:
                self.warnings.append("PPPoE WAN should have password_ref for security")

        elif wan.type == "static":
            if not wan.ip:
                self.errors.append("Static WAN requires ip address")
            if not wan.netmask:
                self.errors.append("Static WAN requires netmask")
            if not wan.gateway:
                self.errors.append("Static WAN requires gateway")

    def _check_wifi_lan_references(self) -> None:
        """Verify WiFi configurations reference existing LANs."""
        lan_names = {lan.name for lan in self.policy.lans}

        for wifi in self.policy.wifi:
            if wifi.lan not in lan_names:
                self.errors.append(f"WiFi '{wifi.name}' references non-existent LAN '{wifi.lan}'")

            # Check for WiFi security
            if wifi.security:
                if wifi.security.encryption in ["wpa-psk", "wpa2-psk", "wpa3-psk"]:
                    if not wifi.security.password_ref:
                        self.warnings.append(f"WiFi '{wifi.name}' should have password_ref for security")

    def _check_isolation_references(self) -> None:
        """Verify isolation references point to existing LANs."""
        lan_names = {lan.name for lan in self.policy.lans}

        for lan in self.policy.lans:
            for isolated_name in lan.isolated_from:
                if isolated_name not in lan_names:
                    self.errors.append(
                        f"LAN '{lan.name}' isolation references non-existent LAN '{isolated_name}'"
                    )

    def _check_firewall_zone_references(self) -> None:
        """Verify firewall rules reference valid zones."""
        if not self.policy.firewall:
            return

        # Valid zones: wan, lan names, vpn
        valid_zones: Set[str] = {"wan"}
        valid_zones.update(lan.name for lan in self.policy.lans)

        if self.policy.vpn:
            valid_zones.add("vpn")

        for rule in self.policy.firewall.rules:
            for zone in rule.from_zones:
                if zone not in valid_zones:
                    self.errors.append(f"Firewall rule '{rule.name}' references unknown zone '{zone}' in 'from'")

            for zone in rule.to_zones:
                if zone not in valid_zones:
                    self.errors.append(f"Firewall rule '{rule.name}' references unknown zone '{zone}' in 'to'")

    def _check_vpn_conflicts(self) -> None:
        """Check for VPN configuration conflicts."""
        listen_ports = []

        for vpn in self.policy.vpn:
            if vpn.role == "server" and vpn.listen_port:
                if vpn.listen_port in listen_ports:
                    self.errors.append(f"Duplicate VPN listen port: {vpn.listen_port}")
                listen_ports.append(vpn.listen_port)

                # Check port range
                if vpn.listen_port < 1024:
                    self.warnings.append(
                        f"VPN listen port {vpn.listen_port} is privileged (<1024), may require root"
                    )

    def _check_nat_port_forwards(self) -> None:
        """Validate NAT port forwarding configuration."""
        if not self.policy.nat or not self.policy.nat.port_forwards:
            return

        # Check internal IPs are in LAN subnets
        lan_networks = []
        for lan in self.policy.lans:
            try:
                network = ipaddress.ip_network(lan.subnet, strict=False)
                lan_networks.append((lan.name, network))
            except ValueError:
                pass  # Already reported in subnet check

        for pf in self.policy.nat.port_forwards:
            try:
                internal_ip = ipaddress.ip_address(pf.internal_ip)
                found = False

                for lan_name, network in lan_networks:
                    if internal_ip in network:
                        found = True
                        break

                if not found:
                    self.warnings.append(
                        f"Port forward to {pf.internal_ip} is not in any defined LAN subnet"
                    )

            except ValueError:
                self.errors.append(f"Invalid internal IP in port forward: {pf.internal_ip}")

    def validate(self) -> None:
        """
        Run all semantic validations.

        Raises:
            ValidationError: If validation errors are found
        """
        self.errors = []
        self.warnings = []

        # Run all validation checks
        self._check_subnet_overlaps()
        self._check_gateway_in_subnet()
        self._check_dhcp_ranges()
        self._check_wan_required_fields()
        self._check_wifi_lan_references()
        self._check_isolation_references()
        self._check_firewall_zone_references()
        self._check_vpn_conflicts()
        self._check_nat_port_forwards()

        if self.errors:
            error_msg = "Policy validation failed:\n" + "\n".join(f"  - {e}" for e in self.errors)
            if self.warnings:
                error_msg += "\n\nWarnings:\n" + "\n".join(f"  - {w}" for w in self.warnings)
            raise ValidationError(error_msg)

    def get_warnings(self) -> List[str]:
        """Get validation warnings (non-fatal issues)."""
        return self.warnings


def validate_policy(policy: Policy) -> None:
    """
    Validate a policy instance.

    Args:
        policy: Policy to validate

    Raises:
        ValidationError: If validation fails
    """
    validator = PolicyValidator(policy)
    validator.validate()
