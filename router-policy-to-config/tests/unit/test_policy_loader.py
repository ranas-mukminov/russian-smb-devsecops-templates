"""Test policy loader functionality."""

import pytest
import yaml
from pathlib import Path

from router_policy_to_config.policy_loader import PolicyLoader, PolicyLoadError


def test_load_valid_policy(tmp_path):
    """Test loading a valid policy file."""
    policy_content = """
meta:
  name: test-policy
  target:
    vendor: routeros

wan:
  type: dhcp
  interface: ether1

lans:
  - name: main
    subnet: 192.168.1.0/24
    gateway: 192.168.1.1
"""
    
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text(policy_content)
    
    loader = PolicyLoader()
    policy = loader.load(str(policy_file))
    
    assert policy.meta.name == "test-policy"
    assert policy.meta.target.vendor == "routeros"
    assert policy.wan.type == "dhcp"
    assert len(policy.lans) == 1
    assert policy.lans[0].name == "main"


def test_load_nonexistent_file():
    """Test loading a non-existent file raises error."""
    loader = PolicyLoader()
    
    with pytest.raises(PolicyLoadError, match="not found"):
        loader.load("nonexistent.yaml")


def test_load_invalid_yaml(tmp_path):
    """Test loading invalid YAML raises error."""
    policy_file = tmp_path / "invalid.yaml"
    policy_file.write_text("invalid: yaml: content:")
    
    loader = PolicyLoader()
    
    with pytest.raises(PolicyLoadError, match="Failed to parse YAML"):
        loader.load(str(policy_file))


def test_schema_validation_missing_required_field(tmp_path):
    """Test schema validation catches missing required fields."""
    policy_content = """
meta:
  name: test

# Missing wan section
lans:
  - name: main
    subnet: 192.168.1.0/24
    gateway: 192.168.1.1
"""
    
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text(policy_content)
    
    loader = PolicyLoader()
    
    # Should fail schema validation
    with pytest.raises(PolicyLoadError, match="validation failed"):
        loader.load(str(policy_file))


def test_secret_resolution():
    """Test secret reference resolution."""
    import os
    
    # Set test secret
    os.environ["SECRET_TEST_PASSWORD"] = "test123"
    
    policy_data = {
        "meta": {"name": "test", "target": {"vendor": "routeros"}},
        "wan": {
            "type": "pppoe",
            "interface": "ether1",
            "username": "user",
            "password_ref": "secret:test_password"
        }
    }
    
    loader = PolicyLoader()
    resolved = loader._resolve_secrets(policy_data)
    
    assert resolved["wan"]["password_ref"] == "test123"
    
    # Clean up
    del os.environ["SECRET_TEST_PASSWORD"]


def test_to_model_conversion():
    """Test conversion from dict to Policy model."""
    policy_data = {
        "meta": {
            "name": "test-router",
            "description": "Test description",
            "target": {"vendor": "routeros", "version": "v7"}
        },
        "wan": {
            "type": "dhcp",
            "interface": "ether1"
        },
        "lans": [
            {
                "name": "main",
                "subnet": "192.168.1.0/24",
                "gateway": "192.168.1.1",
                "dhcp": {
                    "enabled": True,
                    "range": "192.168.1.100-192.168.1.200"
                }
            }
        ]
    }
    
    loader = PolicyLoader()
    policy = loader.to_model(policy_data)
    
    assert policy.meta.name == "test-router"
    assert policy.meta.description == "Test description"
    assert policy.meta.target.vendor == "routeros"
    assert policy.meta.target.version == "v7"
    assert policy.wan.type == "dhcp"
    assert len(policy.lans) == 1
    assert policy.lans[0].dhcp.enabled is True
