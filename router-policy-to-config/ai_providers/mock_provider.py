"""
Mock AI provider for testing.

Returns deterministic responses for testing without actual AI API calls.
"""

from typing import Any, Dict, List, Optional

from ai_providers.base import AIProvider


class MockProvider(AIProvider):
    """Mock AI provider that returns deterministic responses."""

    def __init__(self):
        """Initialize mock provider."""
        self.call_count = 0

    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate a mock completion.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            Mock generated text
        """
        self.call_count += 1

        # Return different responses based on prompt keywords
        if "router policy YAML" in prompt or "Generate a router policy" in prompt:
            return self._generate_mock_policy()
        elif "test cases" in prompt.lower():
            return self._generate_mock_test_cases()
        else:
            return "Mock AI response for testing purposes."

    def is_available(self) -> bool:
        """Mock provider is always available."""
        return True

    def _generate_mock_policy(self) -> str:
        """Generate a mock policy YAML."""
        return """meta:
  name: mock-home-network
  description: Mock home network configuration for testing
  target:
    vendor: routeros
    version: v7

wan:
  type: pppoe
  interface: ether1
  username: "mock_isp_user"
  password_ref: "secret:pppoe_password"

lans:
  - name: main
    subnet: 192.168.10.0/24
    gateway: 192.168.10.1
    dhcp:
      enabled: true
      range: 192.168.10.100-192.168.10.200

  - name: guest
    subnet: 192.168.20.0/24
    gateway: 192.168.20.1
    dhcp:
      enabled: true
      range: 192.168.20.50-192.168.20.150
    isolated_from:
      - main

wifi:
  - name: main-wifi
    lan: main
    ssid: "MockHome"
    mode: ap
    security:
      encryption: wpa2-psk
      password_ref: "secret:wifi_main_password"

firewall:
  default_policy: drop
  rules:
    - name: allow_lan_to_internet
      from: [main]
      to: [wan]
      action: accept
    - name: block_guest_to_main
      from: [guest]
      to: [main]
      action: drop
"""

    def _generate_mock_test_cases(self) -> str:
        """Generate mock test cases JSON."""
        return """[
  {
    "name": "test_main_lan_internet",
    "description": "Verify main LAN has internet access",
    "type": "connectivity",
    "steps": [
      "ping -c 4 8.8.8.8 from main LAN",
      "curl -I http://example.com from main LAN"
    ],
    "expected": "successful connection and DNS resolution"
  },
  {
    "name": "test_guest_isolation",
    "description": "Verify guest network cannot reach main LAN",
    "type": "firewall",
    "steps": [
      "ping main LAN gateway from guest network",
      "attempt SSH to main LAN host from guest"
    ],
    "expected": "connection refused or timeout"
  },
  {
    "name": "test_guest_internet",
    "description": "Verify guest network has internet access",
    "type": "connectivity",
    "steps": [
      "ping -c 4 8.8.8.8 from guest network",
      "curl -I http://example.com from guest"
    ],
    "expected": "successful connection"
  }
]"""
