"""Test policy validator functionality."""

import pytest

from router_policy_to_config.model import (
    DHCPConfig, Firewall, FirewallRule, LANConfig, Meta, Policy, Target, WANConfig
)
from router_policy_to_config.policy_validator import PolicyValidator, ValidationError


def test_subnet_overlap_detection():
    """Test detection of overlapping subnets."""
    policy = Policy(
        meta=Meta(name="test", target=Target(vendor="routeros")),
        wan=WANConfig(type="dhcp", interface="ether1"),
        lans=[
            LANConfig(name="lan1", subnet="192.168.1.0/24", gateway="192.168.1.1"),
            LANConfig(name="lan2", subnet="192.168.1.0/25", gateway="192.168.1.129"),
        ]
    )
    
    validator = PolicyValidator(policy)
    
    with pytest.raises(ValidationError, match="overlap"):
        validator.validate()


def test_gateway_in_subnet():
    """Test gateway IP is within subnet."""
    policy = Policy(
        meta=Meta(name="test", target=Target(vendor="routeros")),
        wan=WANConfig(type="dhcp", interface="ether1"),
        lans=[
            LANConfig(name="lan1", subnet="192.168.1.0/24", gateway="192.168.2.1"),  # Wrong subnet
        ]
    )
    
    validator = PolicyValidator(policy)
    
    with pytest.raises(ValidationError, match="not in subnet"):
        validator.validate()


def test_dhcp_range_validation():
    """Test DHCP range is within subnet."""
    dhcp = DHCPConfig(enabled=True, range="192.168.2.100-192.168.2.200")
    policy = Policy(
        meta=Meta(name="test", target=Target(vendor="routeros")),
        wan=WANConfig(type="dhcp", interface="ether1"),
        lans=[
            LANConfig(name="lan1", subnet="192.168.1.0/24", gateway="192.168.1.1", dhcp=dhcp),
        ]
    )
    
    validator = PolicyValidator(policy)
    
    with pytest.raises(ValidationError, match="DHCP range"):
        validator.validate()


def test_pppoe_requires_username():
    """Test PPPoE WAN requires username."""
    policy = Policy(
        meta=Meta(name="test", target=Target(vendor="routeros")),
        wan=WANConfig(type="pppoe", interface="ether1"),  # Missing username
        lans=[]
    )
    
    validator = PolicyValidator(policy)
    
    with pytest.raises(ValidationError, match="username"):
        validator.validate()


def test_valid_policy_passes():
    """Test a valid policy passes all checks."""
    dhcp = DHCPConfig(enabled=True, range="192.168.1.100-192.168.1.200")
    policy = Policy(
        meta=Meta(name="test", target=Target(vendor="routeros")),
        wan=WANConfig(type="dhcp", interface="ether1"),
        lans=[
            LANConfig(name="main", subnet="192.168.1.0/24", gateway="192.168.1.1", dhcp=dhcp),
        ]
    )
    
    validator = PolicyValidator(policy)
    validator.validate()  # Should not raise


def test_wifi_lan_reference_validation():
    """Test WiFi references existing LAN."""
    from router_policy_to_config.model import WiFiConfig, SecurityConfig
    
    policy = Policy(
        meta=Meta(name="test", target=Target(vendor="routeros")),
        wan=WANConfig(type="dhcp", interface="ether1"),
        lans=[
            LANConfig(name="main", subnet="192.168.1.0/24", gateway="192.168.1.1"),
        ],
        wifi=[
            WiFiConfig(
                name="wifi1",
                lan="nonexistent",  # Invalid reference
                ssid="TestSSID",
                mode="ap",
                security=SecurityConfig(encryption="wpa2-psk", password_ref="secret:wifi")
            )
        ]
    )
    
    validator = PolicyValidator(policy)
    
    with pytest.raises(ValidationError, match="non-existent LAN"):
        validator.validate()


def test_isolation_reference_validation():
    """Test isolation references valid LANs."""
    policy = Policy(
        meta=Meta(name="test", target=Target(vendor="routeros")),
        wan=WANConfig(type="dhcp", interface="ether1"),
        lans=[
            LANConfig(
                name="guest",
                subnet="192.168.2.0/24",
                gateway="192.168.2.1",
                isolated_from=["nonexistent"]  # Invalid reference
            ),
        ]
    )
    
    validator = PolicyValidator(policy)
    
    with pytest.raises(ValidationError, match="non-existent LAN"):
        validator.validate()


def test_firewall_zone_validation():
    """Test firewall rules reference valid zones."""
    policy = Policy(
        meta=Meta(name="test", target=Target(vendor="routeros")),
        wan=WANConfig(type="dhcp", interface="ether1"),
        lans=[
            LANConfig(name="main", subnet="192.168.1.0/24", gateway="192.168.1.1"),
        ],
        firewall=Firewall(
            rules=[
                FirewallRule(
                    name="test-rule",
                    from_zones=["invalid-zone"],  # Invalid zone
                    to_zones=["wan"],
                    action="accept"
                )
            ]
        )
    )
    
    validator = PolicyValidator(policy)
    
    with pytest.raises(ValidationError, match="unknown zone"):
        validator.validate()
