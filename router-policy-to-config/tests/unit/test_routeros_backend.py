"""Test RouterOS backend functionality."""

import pytest

from router_policy_to_config.model import (
    DHCPConfig, LANConfig, Meta, Policy, Target, WANConfig
)
from router_policy_to_config.backends.routeros_backend import RouterOSBackend


def test_routeros_backend_basic_generation():
    """Test basic RouterOS config generation."""
    policy = Policy(
        meta=Meta(name="test-router", target=Target(vendor="routeros", version="v7")),
        wan=WANConfig(type="dhcp", interface="ether1"),
        lans=[
            LANConfig(
                name="main",
                subnet="192.168.1.0/24",
                gateway="192.168.1.1",
                dhcp=DHCPConfig(enabled=True, range="192.168.1.100-192.168.1.200")
            )
        ]
    )
    
    backend = RouterOSBackend(policy)
    config = backend.generate()
    
    assert isinstance(config, str)
    assert len(config) > 0
    assert "RouterOS Configuration" in config
    assert "test-router" in config
    assert "dhcp-client" in config or "ether1" in config
    assert "bridge-lan" in config
    assert "192.168.1.1" in config


def test_routeros_pppoe_generation():
    """Test PPPoE configuration generation."""
    policy = Policy(
        meta=Meta(name="pppoe-router", target=Target(vendor="routeros")),
        wan=WANConfig(
            type="pppoe",
            interface="ether1",
            username="test_user",
            password_ref="test_password"
        ),
        lans=[]
    )
    
    backend = RouterOSBackend(policy)
    config = backend.generate()
    
    assert "pppoe-client" in config
    assert "test_user" in config
    assert "ether1" in config


def test_routeros_nat_generation():
    """Test NAT configuration generation."""
    from router_policy_to_config.model import NATConfig
    
    policy = Policy(
        meta=Meta(name="nat-router", target=Target(vendor="routeros")),
        wan=WANConfig(type="dhcp", interface="ether1"),
        lans=[
            LANConfig(name="main", subnet="192.168.1.0/24", gateway="192.168.1.1")
        ],
        nat=NATConfig(masquerade=True)
    )
    
    backend = RouterOSBackend(policy)
    config = backend.generate()
    
    assert "firewall nat" in config
    assert "masquerade" in config


def test_routeros_firewall_generation():
    """Test firewall configuration generation."""
    from router_policy_to_config.model import Firewall, FirewallRule
    
    policy = Policy(
        meta=Meta(name="fw-router", target=Target(vendor="routeros")),
        wan=WANConfig(type="dhcp", interface="ether1"),
        lans=[
            LANConfig(name="main", subnet="192.168.1.0/24", gateway="192.168.1.1")
        ],
        firewall=Firewall(
            default_policy="drop",
            rules=[
                FirewallRule(
                    name="allow_lan_internet",
                    from_zones=["main"],
                    to_zones=["wan"],
                    action="accept"
                )
            ]
        )
    )
    
    backend = RouterOSBackend(policy)
    config = backend.generate()
    
    assert "firewall filter" in config
    assert "allow_lan_internet" in config or "accept" in config
