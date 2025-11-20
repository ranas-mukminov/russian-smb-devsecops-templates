"""
Test case generator using AI.

Generates test scenarios based on policy configuration.
"""

import json
from typing import Any, Dict, List, Optional

from router_policy_to_config.ai_providers.base import AIProvider
from router_policy_to_config.ai_providers.mock_provider import MockProvider
from router_policy_to_config.model import Policy


class TestCaseGenerator:
    """Generate test cases for router configurations."""

    def __init__(self, ai_provider: Optional[AIProvider] = None):
        """
        Initialize test case generator.

        Args:
            ai_provider: AI provider to use. If None, uses MockProvider.
        """
        self.ai_provider = ai_provider or MockProvider()

    def _policy_to_summary(self, policy: Policy) -> str:
        """Convert policy to text summary for AI."""
        summary_parts = [
            f"Router: {policy.meta.name}",
            f"Target: {policy.meta.target.vendor} {policy.meta.target.version or ''}",
            f"WAN: {policy.wan.type} on {policy.wan.interface}",
        ]

        if policy.lans:
            summary_parts.append(f"LANs: {len(policy.lans)}")
            for lan in policy.lans:
                isolation = f" (isolated from: {', '.join(lan.isolated_from)})" if lan.isolated_from else ""
                summary_parts.append(f"  - {lan.name}: {lan.subnet}{isolation}")

        if policy.wifi:
            summary_parts.append(f"WiFi: {len(policy.wifi)} network(s)")
            for wifi in policy.wifi:
                guest_str = " (guest)" if wifi.guest else ""
                summary_parts.append(f"  - {wifi.ssid}{guest_str}")

        if policy.vpn:
            summary_parts.append(f"VPN: {len(policy.vpn)} configuration(s)")

        if policy.firewall and policy.firewall.rules:
            summary_parts.append(f"Firewall: {len(policy.firewall.rules)} custom rule(s)")

        return "\n".join(summary_parts)

    def generate_test_cases(self, policy: Policy) -> List[Dict[str, Any]]:
        """
        Generate test cases for a policy.

        Args:
            policy: Policy instance

        Returns:
            List of test case dictionaries
        """
        if not self.ai_provider.is_available():
            return self._generate_basic_test_cases(policy)

        summary = self._policy_to_summary(policy)
        vendor = policy.meta.target.vendor

        test_cases = self.ai_provider.generate_test_cases(summary, vendor)

        # Add deterministic test cases
        basic_cases = self._generate_basic_test_cases(policy)
        test_cases.extend(basic_cases)

        return test_cases

    def _generate_basic_test_cases(self, policy: Policy) -> List[Dict[str, Any]]:
        """Generate basic test cases without AI."""
        test_cases = []

        # Internet connectivity tests for each LAN
        for lan in policy.lans:
            test_cases.append({
                "name": f"test_{lan.name}_internet_connectivity",
                "description": f"Verify {lan.name} LAN can reach internet",
                "type": "connectivity",
                "steps": [
                    f"ping -c 4 8.8.8.8 from {lan.name}",
                    f"curl -I http://example.com from {lan.name}"
                ],
                "expected": "successful connection"
            })

        # Isolation tests
        for lan in policy.lans:
            for isolated_lan in lan.isolated_from:
                test_cases.append({
                    "name": f"test_{lan.name}_isolated_from_{isolated_lan}",
                    "description": f"Verify {lan.name} cannot reach {isolated_lan}",
                    "type": "firewall",
                    "steps": [
                        f"ping gateway of {isolated_lan} from {lan.name}",
                        f"attempt connection to {isolated_lan} subnet"
                    ],
                    "expected": "connection blocked"
                })

        # WiFi connectivity tests
        for wifi in policy.wifi:
            test_cases.append({
                "name": f"test_wifi_{wifi.name}_connectivity",
                "description": f"Verify WiFi {wifi.ssid} connects to {wifi.lan}",
                "type": "connectivity",
                "steps": [
                    f"connect to SSID '{wifi.ssid}'",
                    f"verify IP in {wifi.lan} subnet",
                    "test internet access"
                ],
                "expected": "successful connection and internet access"
            })

        # VPN tests
        for vpn in policy.vpn:
            if vpn.role == "server":
                test_cases.append({
                    "name": f"test_vpn_{vpn.type}_server",
                    "description": f"Verify {vpn.type} VPN server is accessible",
                    "type": "connectivity",
                    "steps": [
                        f"connect to VPN on port {vpn.listen_port}",
                        "verify tunnel establishment",
                        "test routing through VPN"
                    ],
                    "expected": "successful VPN connection"
                })

        return test_cases

    def export_test_cases(self, test_cases: List[Dict[str, Any]], format: str = "yaml") -> str:
        """
        Export test cases in specified format.

        Args:
            test_cases: List of test case dictionaries
            format: Output format ('yaml' or 'json')

        Returns:
            Formatted test cases as string
        """
        if format == "json":
            return json.dumps(test_cases, indent=2)
        else:
            import yaml
            return yaml.dump(test_cases, default_flow_style=False)
