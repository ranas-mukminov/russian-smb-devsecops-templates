"""
Policy loader module.

Loads and validates YAML policy files against the JSON schema.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import jsonschema
import yaml

from router_policy_to_config.model import (
    DHCPConfig,
    DNSConfig,
    Firewall,
    FirewallRule,
    LANConfig,
    Meta,
    NATConfig,
    Policy,
    PortForward,
    SecurityConfig,
    Target,
    VPNConfig,
    VPNPeer,
    WANConfig,
    WiFiConfig,
)


class PolicyLoadError(Exception):
    """Exception raised when policy loading fails."""

    pass


class PolicyLoader:
    """Load and validate YAML policy files."""

    def __init__(self, schema_path: Optional[str] = None):
        """
        Initialize policy loader.

        Args:
            schema_path: Path to policy schema YAML file. If None, uses default.
        """
        if schema_path is None:
            # Default to schema in the package
            pkg_dir = Path(__file__).parent.parent.parent
            schema_path = pkg_dir / "schema" / "policy-schema.yaml"

        self.schema_path = Path(schema_path)
        self.schema = self._load_schema()

    def _load_schema(self) -> Dict[str, Any]:
        """Load JSON schema from YAML file."""
        if not self.schema_path.exists():
            raise PolicyLoadError(f"Schema file not found: {self.schema_path}")

        with open(self.schema_path, "r") as f:
            return yaml.safe_load(f)

    def _resolve_secrets(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve secret references in the policy.

        Looks for fields ending with _ref containing "secret:key_name"
        and resolves them from environment variables.

        Args:
            data: Policy data dictionary

        Returns:
            Data with resolved secrets
        """

        def resolve_value(value: Any) -> Any:
            if isinstance(value, str) and value.startswith("secret:"):
                secret_key = value.replace("secret:", "")
                env_key = f"SECRET_{secret_key.upper()}"
                secret_value = os.environ.get(env_key)
                if secret_value is None:
                    # Return placeholder for testing/validation
                    return f"<{env_key}_NOT_SET>"
                return secret_value
            elif isinstance(value, dict):
                return {k: resolve_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [resolve_value(item) for item in value]
            return value

        return resolve_value(data)

    def load_yaml(self, path: str) -> Dict[str, Any]:
        """
        Load YAML policy file.

        Args:
            path: Path to YAML policy file

        Returns:
            Policy data as dictionary

        Raises:
            PolicyLoadError: If file cannot be loaded or parsed
        """
        policy_path = Path(path)
        if not policy_path.exists():
            raise PolicyLoadError(f"Policy file not found: {path}")

        try:
            with open(policy_path, "r") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise PolicyLoadError(f"Failed to parse YAML: {e}")

        return data

    def validate_schema(self, data: Dict[str, Any]) -> None:
        """
        Validate policy data against JSON schema.

        Args:
            data: Policy data dictionary

        Raises:
            PolicyLoadError: If validation fails
        """
        try:
            jsonschema.validate(instance=data, schema=self.schema)
        except jsonschema.ValidationError as e:
            raise PolicyLoadError(f"Schema validation failed: {e.message}")
        except jsonschema.SchemaError as e:
            raise PolicyLoadError(f"Invalid schema: {e.message}")

    def _parse_dhcp(self, data: Dict[str, Any]) -> DHCPConfig:
        """Parse DHCP configuration."""
        return DHCPConfig(
            enabled=data.get("enabled", False),
            range=data.get("range"),
            lease_time=data.get("lease_time", "24h"),
            dns_servers=data.get("dns_servers", []),
        )

    def _parse_security(self, data: Dict[str, Any]) -> SecurityConfig:
        """Parse WiFi security configuration."""
        return SecurityConfig(
            encryption=data["encryption"],
            password_ref=data.get("password_ref"),
            radius_server=data.get("radius_server"),
            radius_secret_ref=data.get("radius_secret_ref"),
        )

    def _parse_vpn_peer(self, data: Dict[str, Any]) -> VPNPeer:
        """Parse VPN peer configuration."""
        return VPNPeer(
            name=data["name"],
            public_key_ref=data.get("public_key_ref"),
            allowed_ips=data.get("allowed_ips", []),
        )

    def to_model(self, data: Dict[str, Any]) -> Policy:
        """
        Convert validated policy data to Policy model.

        Args:
            data: Validated policy data dictionary

        Returns:
            Policy model instance
        """
        # Resolve secrets
        data = self._resolve_secrets(data)

        # Parse meta
        meta_data = data["meta"]
        target = Target(
            vendor=meta_data["target"]["vendor"],
            version=meta_data["target"].get("version"),
        )
        meta = Meta(
            name=meta_data["name"],
            description=meta_data.get("description"),
            target=target,
        )

        # Parse WAN
        wan_data = data["wan"]
        wan = WANConfig(
            type=wan_data["type"],
            interface=wan_data["interface"],
            username=wan_data.get("username"),
            password_ref=wan_data.get("password_ref"),
            ip=wan_data.get("ip"),
            netmask=wan_data.get("netmask"),
            gateway=wan_data.get("gateway"),
            dns=wan_data.get("dns", []),
            mtu=wan_data.get("mtu"),
        )

        # Parse LANs
        lans = []
        for lan_data in data.get("lans", []):
            dhcp = None
            if "dhcp" in lan_data:
                dhcp = self._parse_dhcp(lan_data["dhcp"])

            lan = LANConfig(
                name=lan_data["name"],
                subnet=lan_data["subnet"],
                gateway=lan_data["gateway"],
                vlan_id=lan_data.get("vlan_id"),
                interface=lan_data.get("interface"),
                dhcp=dhcp,
                isolated_from=lan_data.get("isolated_from", []),
            )
            lans.append(lan)

        # Parse WiFi
        wifi_configs = []
        for wifi_data in data.get("wifi", []):
            security = None
            if "security" in wifi_data:
                security = self._parse_security(wifi_data["security"])

            wifi = WiFiConfig(
                name=wifi_data["name"],
                lan=wifi_data["lan"],
                ssid=wifi_data["ssid"],
                mode=wifi_data["mode"],
                channel=wifi_data.get("channel"),
                band=wifi_data.get("band"),
                hidden=wifi_data.get("hidden", False),
                guest=wifi_data.get("guest", False),
                security=security,
            )
            wifi_configs.append(wifi)

        # Parse VPN
        vpn_configs = []
        for vpn_data in data.get("vpn", []):
            peers = [self._parse_vpn_peer(p) for p in vpn_data.get("peers", [])]

            vpn = VPNConfig(
                type=vpn_data["type"],
                role=vpn_data["role"],
                listen_port=vpn_data.get("listen_port"),
                interface=vpn_data.get("interface"),
                allowed_ips=vpn_data.get("allowed_ips", []),
                endpoint=vpn_data.get("endpoint"),
                public_key_ref=vpn_data.get("public_key_ref"),
                private_key_ref=vpn_data.get("private_key_ref"),
                peers=peers,
            )
            vpn_configs.append(vpn)

        # Parse Firewall
        firewall = None
        if "firewall" in data:
            fw_data = data["firewall"]
            rules = []
            for rule_data in fw_data.get("rules", []):
                rule = FirewallRule(
                    name=rule_data["name"],
                    action=rule_data["action"],
                    from_zones=rule_data.get("from", []),
                    to_zones=rule_data.get("to", []),
                    protocol=rule_data.get("protocol"),
                    port=rule_data.get("port"),
                    state=rule_data.get("state", []),
                    log=rule_data.get("log", False),
                    comment=rule_data.get("comment"),
                )
                rules.append(rule)

            firewall = Firewall(
                default_policy=fw_data.get("default_policy", "drop"),
                rules=rules,
            )

        # Parse DNS
        dns = None
        if "dns" in data:
            dns_data = data["dns"]
            dns = DNSConfig(
                servers=dns_data.get("servers", []),
                domain=dns_data.get("domain"),
                forwarders=dns_data.get("forwarders", []),
            )

        # Parse NAT
        nat = None
        if "nat" in data:
            nat_data = data["nat"]
            port_forwards = []
            for pf_data in nat_data.get("port_forwards", []):
                pf = PortForward(
                    name=pf_data.get("name"),
                    protocol=pf_data.get("protocol", "tcp"),
                    external_port=pf_data["external_port"],
                    internal_ip=pf_data["internal_ip"],
                    internal_port=pf_data["internal_port"],
                )
                port_forwards.append(pf)

            nat = NATConfig(
                masquerade=nat_data.get("masquerade", True),
                port_forwards=port_forwards,
            )

        return Policy(
            meta=meta,
            wan=wan,
            lans=lans,
            wifi=wifi_configs,
            vpn=vpn_configs,
            firewall=firewall,
            dns=dns,
            nat=nat,
        )

    def load(self, path: str, validate: bool = True) -> Policy:
        """
        Load and parse policy file.

        Args:
            path: Path to YAML policy file
            validate: Whether to validate against schema

        Returns:
            Policy model instance

        Raises:
            PolicyLoadError: If loading or validation fails
        """
        data = self.load_yaml(path)

        if validate:
            self.validate_schema(data)

        return self.to_model(data)


# Convenience function for quick loading
def load_policy(path: str, schema_path: Optional[str] = None) -> Policy:
    """
    Load policy from YAML file.

    Args:
        path: Path to policy YAML file
        schema_path: Optional path to schema file

    Returns:
        Policy instance
    """
    loader = PolicyLoader(schema_path=schema_path)
    return loader.load(path)
