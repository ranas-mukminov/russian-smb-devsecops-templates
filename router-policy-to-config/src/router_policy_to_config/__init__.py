"""
Router Policy to Config - Core Package

AI-assisted copilot for router configuration.
Transform YAML policies into vendor-specific router configs.
"""

__version__ = "0.1.0"
__author__ = "run-as-daemon"
__license__ = "Apache-2.0"

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
    WANConfig,
    WiFiConfig,
)

__all__ = [
    "Policy",
    "Meta",
    "Target",
    "WANConfig",
    "LANConfig",
    "DHCPConfig",
    "WiFiConfig",
    "SecurityConfig",
    "VPNConfig",
    "Firewall",
    "FirewallRule",
    "DNSConfig",
    "NATConfig",
    "PortForward",
]
