"""
RouterOS backend for generating MikroTik RouterOS configuration.

Generates .rsc scripts compatible with RouterOS v6 and v7.
"""

import ipaddress
from typing import List

from router_policy_to_config.model import Policy


class RouterOSBackend:
    """Generate RouterOS configuration from policy."""

    def __init__(self, policy: Policy):
        """
        Initialize RouterOS backend.

        Args:
            policy: Policy instance to convert
        """
        self.policy = policy
        self.commands: List[str] = []
        self.version = policy.meta.target.version or "v7"

    def _add_comment(self, text: str) -> None:
        """Add a comment to the configuration."""
        self.commands.append(f"# {text}")

    def _add_command(self, command: str) -> None:
        """Add a command to the configuration."""
        self.commands.append(command)

    def _add_blank(self) -> None:
        """Add a blank line for readability."""
        self.commands.append("")

    def _generate_wan(self) -> None:
        """Generate WAN configuration."""
        self._add_comment(f"WAN Configuration ({self.policy.wan.type})")

        wan = self.policy.wan

        if wan.type == "pppoe":
            # Create PPPoE client
            password = wan.password_ref or "<PASSWORD_NOT_SET>"
            self._add_command(
                f"/interface pppoe-client add "
                f"name=pppoe-out1 "
                f"interface={wan.interface} "
                f"user=\"{wan.username}\" "
                f"password=\"{password}\" "
                f"add-default-route=yes "
                f"use-peer-dns=yes "
                f"disabled=no"
            )

            if wan.mtu:
                self._add_command(f"/interface pppoe-client set pppoe-out1 mtu={wan.mtu}")

        elif wan.type == "dhcp":
            # Configure DHCP client on WAN interface
            self._add_command(
                f"/ip dhcp-client add "
                f"interface={wan.interface} "
                f"add-default-route=yes "
                f"use-peer-dns=yes "
                f"disabled=no"
            )

        elif wan.type == "static":
            # Static IP configuration
            self._add_command(f"/ip address add address={wan.ip}/{wan.netmask} interface={wan.interface}")

            if wan.gateway:
                self._add_command(f"/ip route add dst-address=0.0.0.0/0 gateway={wan.gateway}")

            if wan.dns:
                for dns_server in wan.dns:
                    self._add_command(f"/ip dns set servers={','.join(wan.dns)}")
                    break  # Set all at once

        self._add_blank()

    def _generate_lans(self) -> None:
        """Generate LAN configurations."""
        if not self.policy.lans:
            return

        self._add_comment("LAN Configuration")

        # Create bridge for LANs
        self._add_command("/interface bridge add name=bridge-lan protocol-mode=rstp")
        self._add_blank()

        for lan in self.policy.lans:
            self._add_comment(f"LAN: {lan.name}")

            if lan.vlan_id:
                # VLAN configuration
                self._add_command(
                    f"/interface vlan add name=vlan-{lan.name} vlan-id={lan.vlan_id} interface=bridge-lan"
                )
                interface = f"vlan-{lan.name}"
            else:
                interface = "bridge-lan"

            # Add IP address for gateway
            # Extract netmask from CIDR
            try:
                network = ipaddress.ip_network(lan.subnet, strict=False)
                prefix_len = network.prefixlen
                self._add_command(f"/ip address add address={lan.gateway}/{prefix_len} interface={interface}")
            except ValueError:
                # Fallback
                self._add_command(f"/ip address add address={lan.gateway}/24 interface={interface}")

            # DHCP server
            if lan.dhcp and lan.dhcp.enabled:
                pool_name = f"dhcp-pool-{lan.name}"
                dhcp_range = lan.dhcp.range or "192.168.1.100-192.168.1.200"

                # Create IP pool
                self._add_command(f"/ip pool add name={pool_name} ranges={dhcp_range}")

                # Create DHCP server
                self._add_command(
                    f"/ip dhcp-server add "
                    f"name=dhcp-{lan.name} "
                    f"interface={interface} "
                    f"address-pool={pool_name} "
                    f"lease-time={lan.dhcp.lease_time} "
                    f"disabled=no"
                )

                # Configure DHCP network
                try:
                    network = ipaddress.ip_network(lan.subnet, strict=False)
                    network_addr = str(network.network_address)
                    prefix_len = network.prefixlen
                    dns_servers = ",".join(lan.dhcp.dns_servers) if lan.dhcp.dns_servers else lan.gateway

                    self._add_command(
                        f"/ip dhcp-server network add "
                        f"address={network_addr}/{prefix_len} "
                        f"gateway={lan.gateway} "
                        f"dns-server={dns_servers}"
                    )
                except ValueError:
                    pass

            self._add_blank()

    def _generate_nat(self) -> None:
        """Generate NAT configuration."""
        self._add_comment("NAT Configuration")

        # Determine WAN interface
        wan_interface = "pppoe-out1" if self.policy.wan.type == "pppoe" else self.policy.wan.interface

        # Masquerade for internet access
        if not self.policy.nat or self.policy.nat.masquerade:
            self._add_command(
                f"/ip firewall nat add "
                f"chain=srcnat "
                f"out-interface={wan_interface} "
                f"action=masquerade "
                f"comment=\"NAT for internet access\""
            )

        # Port forwards
        if self.policy.nat and self.policy.nat.port_forwards:
            for pf in self.policy.nat.port_forwards:
                protocol = "tcp,udp" if pf.protocol == "both" else pf.protocol
                comment = f" comment=\"{pf.name}\"" if pf.name else ""

                self._add_command(
                    f"/ip firewall nat add "
                    f"chain=dstnat "
                    f"protocol={protocol} "
                    f"dst-port={pf.external_port} "
                    f"in-interface={wan_interface} "
                    f"action=dst-nat "
                    f"to-addresses={pf.internal_ip} "
                    f"to-ports={pf.internal_port}"
                    f"{comment}"
                )

        self._add_blank()

    def _generate_firewall(self) -> None:
        """Generate firewall configuration."""
        self._add_comment("Firewall Configuration")

        wan_interface = "pppoe-out1" if self.policy.wan.type == "pppoe" else self.policy.wan.interface

        # Basic protection rules (RouterOS best practices)
        self._add_command(
            "/ip firewall filter add "
            "chain=input "
            "connection-state=established,related "
            "action=accept "
            "comment=\"Accept established/related\""
        )

        self._add_command(
            "/ip firewall filter add "
            "chain=input "
            "connection-state=invalid "
            "action=drop "
            "comment=\"Drop invalid\""
        )

        # Allow access from LAN to router
        self._add_command(
            "/ip firewall filter add "
            "chain=input "
            "in-interface=bridge-lan "
            "action=accept "
            "comment=\"Allow LAN to router\""
        )

        # Drop everything else to router (except from WAN for specific services)
        self._add_command(
            "/ip firewall filter add "
            "chain=input "
            "action=drop "
            "comment=\"Drop all other input\""
        )

        # Forward chain - established/related
        self._add_command(
            "/ip firewall filter add "
            "chain=forward "
            "connection-state=established,related "
            "action=accept "
            "comment=\"Accept established/related\""
        )

        self._add_command(
            "/ip firewall filter add "
            "chain=forward "
            "connection-state=invalid "
            "action=drop "
            "comment=\"Drop invalid\""
        )

        # Custom firewall rules
        if self.policy.firewall:
            for rule in self.policy.firewall.rules:
                # Map zones to interfaces
                from_intf = []
                to_intf = []

                for zone in rule.from_zones:
                    if zone == "wan":
                        from_intf.append(wan_interface)
                    elif zone == "vpn":
                        from_intf.append("wireguard1")
                    else:
                        # LAN zone
                        from_intf.append("bridge-lan")

                for zone in rule.to_zones:
                    if zone == "wan":
                        to_intf.append(wan_interface)
                    elif zone == "vpn":
                        to_intf.append("wireguard1")
                    else:
                        to_intf.append("bridge-lan")

                # Build command
                cmd_parts = ["/ip firewall filter add", "chain=forward"]

                if from_intf:
                    cmd_parts.append(f"in-interface={from_intf[0]}")

                if to_intf:
                    cmd_parts.append(f"out-interface={to_intf[0]}")

                if rule.protocol:
                    cmd_parts.append(f"protocol={rule.protocol}")

                if rule.port:
                    cmd_parts.append(f"dst-port={rule.port}")

                cmd_parts.append(f"action={rule.action}")

                if rule.comment:
                    cmd_parts.append(f"comment=\"{rule.comment}\"")
                else:
                    cmd_parts.append(f"comment=\"{rule.name}\"")

                self._add_command(" ".join(cmd_parts))

        # Default drop for forward
        if not self.policy.firewall or self.policy.firewall.default_policy == "drop":
            self._add_command(
                "/ip firewall filter add "
                "chain=forward "
                "action=drop "
                "comment=\"Default drop\""
            )

        self._add_blank()

    def _generate_wifi(self) -> None:
        """Generate WiFi configuration."""
        if not self.policy.wifi:
            return

        self._add_comment("WiFi Configuration")

        for wifi in self.policy.wifi:
            # Create security profile
            if wifi.security:
                profile_name = f"sec-{wifi.name}"
                password = wifi.security.password_ref or "<PASSWORD_NOT_SET>"

                if wifi.security.encryption == "wpa2-psk":
                    self._add_command(
                        f"/interface wireless security-profiles add "
                        f"name={profile_name} "
                        f"mode=dynamic-keys "
                        f"authentication-types=wpa2-psk "
                        f"unicast-ciphers=aes-ccm "
                        f"group-ciphers=aes-ccm "
                        f"wpa2-pre-shared-key=\"{password}\""
                    )

            # Configure wireless interface (assuming wlan1 for first WiFi)
            interface = f"wlan{len(self.commands)}"  # Simple approach
            band_freq = "2ghz-b/g/n" if wifi.band == "2.4ghz" else "5ghz-a/n/ac"

            cmd_parts = [
                f"/interface wireless set {interface}",
                f"disabled=no",
                f"mode=ap-bridge",
                f"ssid=\"{wifi.ssid}\"",
                f"frequency=auto",
                f"band={band_freq}",
            ]

            if wifi.channel:
                cmd_parts.append(f"channel-width=20/40mhz-XX")

            if wifi.security:
                cmd_parts.append(f"security-profile=sec-{wifi.name}")

            if wifi.hidden:
                cmd_parts.append("hide-ssid=yes")

            self._add_command(" ".join(cmd_parts))

        self._add_blank()

    def _generate_vpn(self) -> None:
        """Generate VPN configuration."""
        if not self.policy.vpn:
            return

        for vpn in self.policy.vpn:
            if vpn.type == "wireguard":
                self._add_comment(f"WireGuard VPN ({vpn.role})")

                interface_name = vpn.interface or "wireguard1"

                # Create WireGuard interface
                private_key = vpn.private_key_ref or "<PRIVATE_KEY_NOT_SET>"

                cmd_parts = [
                    "/interface wireguard add",
                    f"name={interface_name}",
                    f"private-key=\"{private_key}\"",
                ]

                if vpn.role == "server" and vpn.listen_port:
                    cmd_parts.append(f"listen-port={vpn.listen_port}")

                self._add_command(" ".join(cmd_parts))

                # Add IP address
                if vpn.allowed_ips:
                    # Use first allowed IP as interface address
                    self._add_command(f"/ip address add address={vpn.allowed_ips[0]} interface={interface_name}")

                # Configure peers
                for peer in vpn.peers:
                    public_key = peer.public_key_ref or "<PUBLIC_KEY_NOT_SET>"
                    allowed_ips = ",".join(peer.allowed_ips) if peer.allowed_ips else "0.0.0.0/0"

                    self._add_command(
                        f"/interface wireguard peers add "
                        f"interface={interface_name} "
                        f"public-key=\"{public_key}\" "
                        f"allowed-address={allowed_ips} "
                        f"comment=\"{peer.name}\""
                    )

                self._add_blank()

    def generate(self) -> str:
        """
        Generate complete RouterOS configuration.

        Returns:
            RouterOS .rsc script as string
        """
        self.commands = []

        # Header
        self._add_comment("=" * 60)
        self._add_comment(f"RouterOS Configuration for: {self.policy.meta.name}")
        self._add_comment(f"Generated by router-policy-to-config")
        self._add_comment(f"Target: RouterOS {self.version}")
        self._add_comment("=" * 60)
        self._add_blank()
        self._add_comment("WARNING: Review this configuration before applying!")
        self._add_comment("Make sure to back up your current configuration first.")
        self._add_blank()

        # Generate sections
        self._generate_wan()
        self._generate_lans()
        self._generate_nat()
        self._generate_firewall()
        self._generate_wifi()
        self._generate_vpn()

        # Footer
        self._add_comment("=" * 60)
        self._add_comment("Configuration complete")
        self._add_comment("Apply with: /import file=thisfile.rsc")
        self._add_comment("=" * 60)

        return "\n".join(self.commands)
