"""
Command-line interface for router-policy-to-config.

Provides subcommands for init, validate, render, diff, ai-suggest, and lab-test.
"""

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.syntax import Syntax
from rich.table import Table

from router_policy_to_config import __version__
from router_policy_to_config.ai.policy_nl_to_yaml import PolicyGenerator
from router_policy_to_config.ai.test_case_generator import TestCaseGenerator
from router_policy_to_config.backends.openwrt_backend import OpenWrtBackend
from router_policy_to_config.backends.routeros_backend import RouterOSBackend
from router_policy_to_config.diff.openwrt_diff import OpenWrtDiff
from router_policy_to_config.diff.routeros_diff import RouterOSDiff
from router_policy_to_config.policy_loader import PolicyLoader, PolicyLoadError
from router_policy_to_config.policy_validator import PolicyValidator, ValidationError

app = typer.Typer(help="AI-assisted copilot for router configuration")
console = Console()


@app.command()
def version():
    """Show version information."""
    console.print(f"router-policy-to-config version {__version__}")
    console.print("https://run-as-daemon.ru")


@app.command()
def init(
    output: str = typer.Option("policy.yaml", "--out", "-o", help="Output policy file"),
    vendor: str = typer.Option("routeros", "--vendor", "-v", help="Target vendor (routeros/openwrt)"),
    interactive: bool = typer.Option(False, "--interactive", "-i", help="Interactive mode"),
):
    """Initialize a new policy file."""
    if interactive:
        console.print("[yellow]Interactive mode not yet implemented. Creating template...[/yellow]")

    # Create template policy
    template = f"""meta:
  name: my-router
  description: My router configuration
  target:
    vendor: {vendor}
    version: v7

wan:
  type: pppoe  # or dhcp, static
  interface: ether1
  username: "YOUR_ISP_USERNAME"
  password_ref: "secret:pppoe_password"

lans:
  - name: main
    subnet: 192.168.10.0/24
    gateway: 192.168.10.1
    dhcp:
      enabled: true
      range: 192.168.10.100-192.168.10.200

firewall:
  default_policy: drop
  rules:
    - name: allow_lan_to_internet
      from: [main]
      to: [wan]
      action: accept
"""

    with open(output, "w") as f:
        f.write(template)

    console.print(f"[green]✓[/green] Created policy template: {output}")
    console.print(f"\nEdit the file and set environment variables for secrets:")
    console.print(f"  export SECRET_PPPOE_PASSWORD='your_password'")


@app.command()
def validate(
    policy_file: str = typer.Argument(..., help="Path to policy YAML file"),
    show_warnings: bool = typer.Option(True, "--warnings/--no-warnings", help="Show warnings"),
):
    """Validate a policy file."""
    try:
        loader = PolicyLoader()
        console.print(f"Loading policy from: {policy_file}")
        policy = loader.load(policy_file)

        console.print("[green]✓[/green] Schema validation passed")

        # Semantic validation
        validator = PolicyValidator(policy)
        validator.validate()

        console.print("[green]✓[/green] Semantic validation passed")

        if show_warnings and validator.warnings:
            console.print("\n[yellow]Warnings:[/yellow]")
            for warning in validator.warnings:
                console.print(f"  ⚠ {warning}")

        console.print(f"\n[green]Policy is valid![/green]")
        console.print(f"  Target: {policy.meta.target.vendor}")
        console.print(f"  LANs: {len(policy.lans)}")
        console.print(f"  WiFi: {len(policy.wifi)}")
        console.print(f"  VPN: {len(policy.vpn)}")

    except (PolicyLoadError, ValidationError) as e:
        console.print(f"[red]✗ Validation failed:[/red]")
        console.print(f"  {e}")
        raise typer.Exit(1)


@app.command()
def render(
    policy_file: str = typer.Argument(..., help="Path to policy YAML file"),
    target: str = typer.Option(..., "--target", "-t", help="Target vendor (routeros/openwrt)"),
    output: Optional[str] = typer.Option(None, "--out", "-o", help="Output file or directory"),
):
    """Render policy to vendor-specific configuration."""
    try:
        loader = PolicyLoader()
        policy = loader.load(policy_file)

        # Override target if specified
        if target:
            policy.meta.target.vendor = target

        console.print(f"Rendering policy for: {policy.meta.target.vendor}")

        if policy.meta.target.vendor == "routeros":
            backend = RouterOSBackend(policy)
            config = backend.generate()

            if output:
                with open(output, "w") as f:
                    f.write(config)
                console.print(f"[green]✓[/green] Configuration written to: {output}")
            else:
                syntax = Syntax(config, "routeros", theme="monokai", line_numbers=False)
                console.print(syntax)

        elif policy.meta.target.vendor == "openwrt":
            backend = OpenWrtBackend(policy)
            configs = backend.generate()

            if output:
                output_dir = Path(output)
                output_dir.mkdir(parents=True, exist_ok=True)

                for filename, content in configs.items():
                    file_path = output_dir / filename
                    with open(file_path, "w") as f:
                        f.write(content)
                    console.print(f"[green]✓[/green] Written: {file_path}")
            else:
                for filename, content in configs.items():
                    console.print(f"\n[bold]--- {filename} ---[/bold]")
                    syntax = Syntax(content, "ini", theme="monokai", line_numbers=False)
                    console.print(syntax)

        else:
            console.print(f"[red]Unknown vendor: {policy.meta.target.vendor}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]✗ Rendering failed:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def diff(
    policy_file: str = typer.Argument(..., help="Path to policy YAML file"),
    target: str = typer.Option(..., "--target", "-t", help="Target vendor"),
    current: str = typer.Option(..., "--current", "-c", help="Current config file/directory"),
    output_json: Optional[str] = typer.Option(None, "--json", help="Export diff as JSON"),
):
    """Compare generated config with current configuration."""
    try:
        loader = PolicyLoader()
        policy = loader.load(policy_file)
        policy.meta.target.vendor = target

        console.print(f"Computing diff for: {target}")

        if target == "routeros":
            backend = RouterOSBackend(policy)
            generated_config = backend.generate()

            with open(current, "r") as f:
                current_config = f.read()

            diff_engine = RouterOSDiff(current_config, generated_config)

            if output_json:
                with open(output_json, "w") as f:
                    f.write(diff_engine.to_json())
                console.print(f"[green]✓[/green] Diff exported to: {output_json}")
            else:
                summary = diff_engine.get_summary()
                console.print(summary)

        elif target == "openwrt":
            backend = OpenWrtBackend(policy)
            generated_configs = backend.generate()

            # Load current configs
            current_dir = Path(current)
            current_configs = {}

            if current_dir.is_dir():
                for filename in ["network", "wireless", "firewall", "dhcp"]:
                    config_file = current_dir / filename
                    if config_file.exists():
                        with open(config_file, "r") as f:
                            current_configs[filename] = f.read()

            diff_engine = OpenWrtDiff(current_configs, generated_configs)

            if output_json:
                with open(output_json, "w") as f:
                    f.write(diff_engine.to_json())
                console.print(f"[green]✓[/green] Diff exported to: {output_json}")
            else:
                summary = diff_engine.get_summary()
                console.print(summary)

        else:
            console.print(f"[red]Unknown vendor: {target}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]✗ Diff failed:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def ai_suggest(
    from_text: Optional[str] = typer.Option(None, "--from-text", help="Text file with description"),
    description: Optional[str] = typer.Option(None, "--desc", "-d", help="Direct description"),
    output: str = typer.Option("policy.yaml", "--out", "-o", help="Output file"),
):
    """Generate policy from natural language description using AI."""
    if not from_text and not description:
        console.print("[red]Error: Provide either --from-text or --desc[/red]")
        raise typer.Exit(1)

    try:
        if from_text:
            with open(from_text, "r") as f:
                description = f.read()

        console.print("[yellow]Generating policy with AI...[/yellow]")
        generator = PolicyGenerator()
        policy_yaml = generator.generate_from_text(description)

        with open(output, "w") as f:
            f.write(policy_yaml)

        console.print(f"[green]✓[/green] Generated policy: {output}")
        console.print(f"\n[yellow]Please review and validate before using![/yellow]")
        console.print(f"  router-policy validate {output}")

    except Exception as e:
        console.print(f"[red]✗ Generation failed:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def lab_test(
    policy_file: str = typer.Argument(..., help="Path to policy YAML file"),
):
    """Run lab tests with the policy (placeholder)."""
    console.print("[yellow]Lab testing not yet implemented.[/yellow]")
    console.print("This feature will:")
    console.print("  - Start Docker lab environment")
    console.print("  - Apply generated configs")
    console.print("  - Run connectivity and firewall tests")
    console.print("  - Report results")


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
