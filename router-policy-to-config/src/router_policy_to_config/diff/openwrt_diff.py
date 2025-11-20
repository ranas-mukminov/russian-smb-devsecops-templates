"""
OpenWrt UCI configuration diff module.

Compare generated UCI configuration with existing configs.
"""

import difflib
import json
from typing import Dict, List


class OpenWrtDiff:
    """Diff engine for OpenWrt UCI configurations."""

    def __init__(self, current_configs: Dict[str, str], generated_configs: Dict[str, str]):
        """
        Initialize diff engine.

        Args:
            current_configs: Dict of filename -> current UCI config content
            generated_configs: Dict of filename -> generated UCI config content
        """
        self.current = current_configs
        self.generated = generated_configs

    def _parse_uci_config(self, content: str) -> List[Dict]:
        """
        Parse UCI config into structured sections.

        Returns list of config sections as dicts.
        """
        sections = []
        current_section = None

        for line in content.split("\n"):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue

            if line.startswith("config "):
                # New section
                if current_section:
                    sections.append(current_section)
                
                parts = line.split(maxsplit=2)
                section_type = parts[1] if len(parts) > 1 else ""
                section_name = parts[2].strip("'\"") if len(parts) > 2 else ""
                
                current_section = {
                    "type": section_type,
                    "name": section_name,
                    "options": []
                }
            elif line.startswith("option ") or line.startswith("list "):
                # Option in current section
                if current_section:
                    current_section["options"].append(line)

        # Add last section
        if current_section:
            sections.append(current_section)

        return sections

    def _compare_configs(self, current: str, generated: str) -> Dict:
        """
        Compare two UCI config files.

        Returns dict with differences.
        """
        current_lines = [line.strip() for line in current.split("\n") if line.strip() and not line.strip().startswith("#")]
        generated_lines = [line.strip() for line in generated.split("\n") if line.strip() and not line.strip().startswith("#")]

        # Compute diff
        diff = list(difflib.unified_diff(
            current_lines,
            generated_lines,
            fromfile="current",
            tofile="generated",
            lineterm=""
        ))

        added = []
        removed = []

        for line in diff:
            if line.startswith("+") and not line.startswith("+++"):
                added.append(line[1:].strip())
            elif line.startswith("-") and not line.startswith("---"):
                removed.append(line[1:].strip())

        # Parse sections
        current_sections = self._parse_uci_config(current)
        generated_sections = self._parse_uci_config(generated)

        # Find section differences
        current_section_keys = {(s["type"], s["name"]) for s in current_sections}
        generated_section_keys = {(s["type"], s["name"]) for s in generated_sections}

        added_sections = generated_section_keys - current_section_keys
        removed_sections = current_section_keys - generated_section_keys
        common_sections = current_section_keys & generated_section_keys

        modified_sections = []
        for section_key in common_sections:
            current_section = next(s for s in current_sections if (s["type"], s["name"]) == section_key)
            generated_section = next(s for s in generated_sections if (s["type"], s["name"]) == section_key)

            if current_section["options"] != generated_section["options"]:
                modified_sections.append({
                    "type": section_key[0],
                    "name": section_key[1],
                    "current_options": current_section["options"],
                    "generated_options": generated_section["options"]
                })

        return {
            "has_changes": len(added) > 0 or len(removed) > 0,
            "added_lines": added,
            "removed_lines": removed,
            "added_sections": [{"type": t, "name": n} for t, n in added_sections],
            "removed_sections": [{"type": t, "name": n} for t, n in removed_sections],
            "modified_sections": modified_sections,
            "unified_diff": diff
        }

    def compute_diff(self) -> Dict:
        """
        Compute differences across all config files.

        Returns:
            Dict with per-file differences
        """
        all_files = set(self.current.keys()) | set(self.generated.keys())
        file_diffs = {}

        for filename in all_files:
            current_content = self.current.get(filename, "")
            generated_content = self.generated.get(filename, "")

            if current_content or generated_content:
                file_diffs[filename] = self._compare_configs(current_content, generated_content)

        # Overall summary
        has_any_changes = any(fd["has_changes"] for fd in file_diffs.values())

        return {
            "has_changes": has_any_changes,
            "files": file_diffs
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
            "OpenWrt UCI Configuration Differences:",
            "=" * 60,
            ""
        ]

        for filename, file_diff in diff_result["files"].items():
            if not file_diff["has_changes"]:
                continue

            summary_lines.append(f"File: /etc/config/{filename}")
            summary_lines.append("-" * 60)

            if file_diff["added_sections"]:
                summary_lines.append(f"  Added sections: {len(file_diff['added_sections'])}")
                for section in file_diff["added_sections"][:5]:
                    summary_lines.append(f"    + {section['type']} '{section['name']}'")

            if file_diff["removed_sections"]:
                summary_lines.append(f"  Removed sections: {len(file_diff['removed_sections'])}")
                for section in file_diff["removed_sections"][:5]:
                    summary_lines.append(f"    - {section['type']} '{section['name']}'")

            if file_diff["modified_sections"]:
                summary_lines.append(f"  Modified sections: {len(file_diff['modified_sections'])}")
                for section in file_diff["modified_sections"][:3]:
                    summary_lines.append(f"    ~ {section['type']} '{section['name']}'")
                    summary_lines.append(f"      Options changed: {len(section['current_options'])} -> {len(section['generated_options'])}")

            summary_lines.append("")

        summary_lines.append("=" * 60)
        summary_lines.append("Review carefully before applying!")

        return "\n".join(summary_lines)

    def to_json(self) -> str:
        """Export diff as JSON."""
        return json.dumps(self.compute_diff(), indent=2)
