"""Configuration diff modules."""

from router_policy_to_config.diff.routeros_diff import RouterOSDiff
from router_policy_to_config.diff.openwrt_diff import OpenWrtDiff

__all__ = ["RouterOSDiff", "OpenWrtDiff"]
