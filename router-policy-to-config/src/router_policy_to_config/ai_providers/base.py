"""
Base AI provider interface.

Abstract base class for AI providers used in policy generation
and test case suggestions.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate a completion from the AI model.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response

        Returns:
            Generated text completion
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the AI provider is available and configured.

        Returns:
            True if provider can be used
        """
        pass

    def generate_policy_yaml(self, description: str) -> str:
        """
        Generate policy YAML from natural language description.

        Args:
            description: Natural language description of network setup

        Returns:
            Generated YAML policy as string
        """
        system_prompt = """You are a network configuration expert. 
Generate a valid YAML policy for a router configuration based on the user's description.
Use the router-policy-to-config schema. Always use secret references (secret:key_name) for passwords.
Use safe, private IP ranges (RFC1918). Be conservative with firewall rules."""

        prompt = f"""Generate a router policy YAML configuration for:

{description}

Return only the YAML, no explanations. Use this structure:

meta:
  name: descriptive-name
  description: brief description
  target:
    vendor: routeros  # or openwrt
    version: v7

wan:
  type: pppoe  # or dhcp, static
  interface: ether1
  username: "ISP_USERNAME"
  password_ref: "secret:pppoe_password"

lans:
  - name: main
    subnet: 192.168.10.0/24
    gateway: 192.168.10.1
    dhcp:
      enabled: true
      range: 192.168.10.100-192.168.10.200

# Add more sections as needed (wifi, vpn, firewall, etc.)
"""

        return self.generate_completion(prompt, system_prompt=system_prompt, temperature=0.5)

    def generate_test_cases(self, policy_summary: str, vendor: str) -> List[Dict[str, Any]]:
        """
        Generate test case suggestions based on policy.

        Args:
            policy_summary: Summary of the policy configuration
            vendor: Target vendor (routeros or openwrt)

        Returns:
            List of test case specifications
        """
        system_prompt = """You are a network testing expert.
Generate test case specifications for validating router configurations.
Focus on connectivity, firewall rules, isolation, and security."""

        prompt = f"""Generate test cases for this {vendor} router policy:

{policy_summary}

Return a JSON array of test cases with this structure:
[
  {{
    "name": "test_lan_internet_access",
    "description": "Verify LAN can access internet",
    "type": "connectivity",
    "steps": ["ping from LAN to 8.8.8.8", "curl http://example.com"],
    "expected": "successful connection"
  }}
]

Include tests for: connectivity, firewall rules, guest isolation, VPN access.
"""

        response = self.generate_completion(prompt, system_prompt=system_prompt, temperature=0.3)
        
        # Parse JSON response (basic implementation)
        try:
            import json
            return json.loads(response)
        except:
            return []
