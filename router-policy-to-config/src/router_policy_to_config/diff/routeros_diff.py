"""
RouterOS configuration diff module.

Compare generated configuration with existing RouterOS exports.
"""

import difflib
import json
import re
from typing import Dict, List, Tuple


class RouterOSDiff:
    """Diff engine for RouterOS configurations."""

    def __init__(self, current_config: str, generated_config: str):
        """
        Initialize diff engine.

        Args:
            current_config: Current RouterOS configuration (export)
            generated_config: Generated configuration from policy
        """
        self.current = current_config
        self.generated = generated_config

    def _normalize_config(self, config: str) -> List[str]:
        """
        Normalize configuration for comparison.

        Remove comments, empty lines, and standardize whitespace.
        """
        lines = []
        for line in config.split("\n"):
            # Remove inline comments
            line = re.sub(r"#.*$", "", line)
            # Strip whitespace
            line = line.strip()
            # Skip empty lines
            if line:
                lines.append(line)
        return lines

    def _extract_commands(self, config: str) -> Dict[str, List[str]]:
        """
        Extract commands grouped by section.

        Returns dict of section -> list of commands.
        """
        sections = {}
        current_section = "general"
        
        for line in self._normalize_config(config):
            # Detect section starts
            if line.startswith("/"):
                # Extract section from command path
                parts = line.split()
                if parts:
                    section = parts[0].split("/")[1] if "/" in parts[0] else "general"
                    if section not in sections:
                        sections[section] = []
                    sections[section].append(line)
                    current_section = section
            else:
                if current_section not in sections:
                    sections[current_section] = []
                sections[current_section].append(line)
        
        return sections

    def compute_diff(self) -> Dict[str, any]:
        """
        Compute difference between configurations.

        Returns:
            Dict with diff information including added, removed, and modified sections
        """
        current_lines = self._normalize_config(self.current)
        generated_lines = self._normalize_config(self.generated)

        # Compute unified diff
        diff = list(difflib.unified_diff(
            current_lines,
            generated_lines,
            fromfile="current",
            tofile="generated",
            lineterm=""
        ))

        # Analyze differences
        added = []
        removed = []
        modified = []

        for line in diff:
            if line.startswith("+") and not line.startswith("+++"):
                added.append(line[1:].strip())
            elif line.startswith("-") and not line.startswith("---"):
                removed.append(line[1:].strip())

        # Extract sections
        current_sections = self._extract_commands(self.current)
        generated_sections = self._extract_commands(self.generated)

        section_changes = {}
        all_sections = set(current_sections.keys()) | set(generated_sections.keys())

        for section in all_sections:
            current_cmds = set(current_sections.get(section, []))
            generated_cmds = set(generated_sections.get(section, []))

            section_added = generated_cmds - current_cmds
            section_removed = current_cmds - generated_cmds

            if section_added or section_removed:
                section_changes[section] = {
                    "added": list(section_added),
                    "removed": list(section_removed)
                }

        return {
            "has_changes": len(added) > 0 or len(removed) > 0,
            "added_lines": added,
            "removed_lines": removed,
            "section_changes": section_changes,
            "unified_diff": diff
        }

    def get_summary(self) -> str:
        """
        Get human-readable summary of changes.

        Returns:
            Formatted string describing changes
        """
        diff_result = self.compute_diff()

        if not diff_result["has_changes"]:
            return "No changes detected between current and generated configuration."

        summary_lines = [
            "Configuration Differences:",
            "=" * 60,
            ""
        ]

        if diff_result["added_lines"]:
            summary_lines.append(f"Added lines: {len(diff_result['added_lines'])}")
            summary_lines.append("-" * 60)
            for line in diff_result["added_lines"][:10]:  # Show first 10
                summary_lines.append(f"  + {line}")
            if len(diff_result["added_lines"]) > 10:
                summary_lines.append(f"  ... and {len(diff_result['added_lines']) - 10} more")
            summary_lines.append("")

        if diff_result["removed_lines"]:
            summary_lines.append(f"Removed lines: {len(diff_result['removed_lines'])}")
            summary_lines.append("-" * 60)
            for line in diff_result["removed_lines"][:10]:  # Show first 10
                summary_lines.append(f"  - {line}")
            if len(diff_result["removed_lines"]) > 10:
                summary_lines.append(f"  ... and {len(diff_result['removed_lines']) - 10} more")
            summary_lines.append("")

        if diff_result["section_changes"]:
            summary_lines.append("Changes by section:")
            summary_lines.append("-" * 60)
            for section, changes in diff_result["section_changes"].items():
                summary_lines.append(f"\n  Section: {section}")
                if changes["added"]:
                    summary_lines.append(f"    Added: {len(changes['added'])} command(s)")
                if changes["removed"]:
                    summary_lines.append(f"    Removed: {len(changes['removed'])} command(s)")

        summary_lines.append("")
        summary_lines.append("=" * 60)
        summary_lines.append("Review carefully before applying!")

        return "\n".join(summary_lines)

    def to_json(self) -> str:
        """Export diff as JSON."""
        return json.dumps(self.compute_diff(), indent=2)
