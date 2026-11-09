"""Networks allowed to call back-office routes, from ALLOWED_NETWORKS (comma-separated CIDRs)."""

import ipaddress
import os


def _parse_networks(value):
    return tuple(
        ipaddress.ip_network(part.strip()) for part in value.split(",") if part.strip()
    )


ALLOWED_NETWORKS = _parse_networks(os.environ.get("ALLOWED_NETWORKS", ""))


def is_allowed_ip(ip):
    try:
        address = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return any(address in network for network in ALLOWED_NETWORKS)
