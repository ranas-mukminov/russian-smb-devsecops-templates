"""
Natural language to policy YAML converter.

Uses AI to convert text descriptions into policy YAML.
"""

from typing import Optional

import yaml

from router_policy_to_config.ai_providers.base import AIProvider
from router_policy_to_config.ai_providers.mock_provider import MockProvider


class PolicyGenerator:
    """Generate policy YAML from natural language descriptions."""

    def __init__(self, ai_provider: Optional[AIProvider] = None):
        """
        Initialize policy generator.

        Args:
            ai_provider: AI provider to use. If None, uses MockProvider.
        """
        self.ai_provider = ai_provider or MockProvider()

    def generate_from_text(self, description: str) -> str:
        """
        Generate policy YAML from text description.

        Args:
            description: Natural language description of network setup

        Returns:
            Generated YAML policy as string
        """
        if not self.ai_provider.is_available():
            raise RuntimeError("AI provider is not available")

        yaml_content = self.ai_provider.generate_policy_yaml(description)

        # Basic validation - try to parse as YAML
        try:
            yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            raise ValueError(f"Generated content is not valid YAML: {e}")

        return yaml_content

    def refine_policy(self, current_yaml: str, refinement_request: str) -> str:
        """
        Refine existing policy based on additional requirements.

        Args:
            current_yaml: Current policy YAML
            refinement_request: Description of desired changes

        Returns:
            Refined policy YAML
        """
        prompt = f"""Current policy:
```yaml
{current_yaml}
```

Requested changes: {refinement_request}

Generate the updated policy YAML with these changes applied.
Return only the YAML, no explanations.
"""

        system_prompt = "You are a network configuration expert. Refine the router policy based on the user's request."

        refined = self.ai_provider.generate_completion(prompt, system_prompt=system_prompt, temperature=0.3)

        # Validate
        try:
            yaml.safe_load(refined)
        except yaml.YAMLError as e:
            raise ValueError(f"Refined content is not valid YAML: {e}")

        return refined
