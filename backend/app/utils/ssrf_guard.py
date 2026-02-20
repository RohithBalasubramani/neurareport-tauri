"""SSRF (Server-Side Request Forgery) Protection.

Validates URLs before server-side HTTP requests to prevent
internal network scanning and metadata service access.

Blocks:
- Private/reserved IP ranges (RFC 1918, link-local, loopback)
- Cloud metadata endpoints (169.254.169.254, fd00::, etc.)
- DNS rebinding (resolves hostname before allowing request)
- Non-HTTP(S) schemes
"""
from __future__ import annotations

import ipaddress
import logging
import socket
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# IP networks that must never be reached by outbound requests
_BLOCKED_NETWORKS = [
    # IPv4
    ipaddress.ip_network("0.0.0.0/8"),        # "This" network
    ipaddress.ip_network("10.0.0.0/8"),        # RFC 1918
    ipaddress.ip_network("100.64.0.0/10"),     # Shared address space
    ipaddress.ip_network("127.0.0.0/8"),       # Loopback
    ipaddress.ip_network("169.254.0.0/16"),    # Link-local (AWS metadata)
    ipaddress.ip_network("172.16.0.0/12"),     # RFC 1918
    ipaddress.ip_network("192.0.0.0/24"),      # IETF protocol assignments
    ipaddress.ip_network("192.0.2.0/24"),      # TEST-NET-1
    ipaddress.ip_network("192.88.99.0/24"),    # 6to4 relay
    ipaddress.ip_network("192.168.0.0/16"),    # RFC 1918
    ipaddress.ip_network("198.18.0.0/15"),     # Benchmarking
    ipaddress.ip_network("198.51.100.0/24"),   # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),    # TEST-NET-3
    ipaddress.ip_network("224.0.0.0/4"),       # Multicast
    ipaddress.ip_network("240.0.0.0/4"),       # Reserved
    ipaddress.ip_network("255.255.255.255/32"),  # Broadcast
    # IPv6
    ipaddress.ip_network("::1/128"),           # Loopback
    ipaddress.ip_network("fc00::/7"),          # Unique local
    ipaddress.ip_network("fe80::/10"),         # Link-local
    ipaddress.ip_network("::ffff:0:0/96"),     # IPv4-mapped
]

_ALLOWED_SCHEMES = {"http", "https"}


class SSRFError(ValueError):
    """Raised when a URL fails SSRF validation."""


def _is_blocked_ip(ip_str: str) -> bool:
    """Check if an IP address falls within a blocked network."""
    try:
        addr = ipaddress.ip_address(ip_str)
    except ValueError:
        return True  # Unparseable → block
    return any(addr in net for net in _BLOCKED_NETWORKS)


def validate_url(
    url: str,
    *,
    allowed_schemes: set[str] | None = None,
    allow_private: bool = False,
) -> str:
    """Validate a URL is safe for server-side requests.

    Resolves the hostname via DNS and checks the resulting IP against
    blocked networks.  Returns the validated URL on success.

    Args:
        url: The URL to validate.
        allowed_schemes: Permitted URL schemes (default: http, https).
        allow_private: If True, skip IP-range checks (for internal tooling only).

    Returns:
        The validated URL string.

    Raises:
        SSRFError: If the URL is unsafe.
    """
    schemes = allowed_schemes or _ALLOWED_SCHEMES

    try:
        parsed = urlparse(url)
    except Exception as exc:
        raise SSRFError(f"Invalid URL: {exc}") from exc

    if not parsed.scheme or parsed.scheme.lower() not in schemes:
        raise SSRFError(f"Scheme '{parsed.scheme}' not allowed (permitted: {', '.join(sorted(schemes))})")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFError("URL has no hostname")

    if allow_private:
        return url

    # Resolve hostname to IPs and check each one
    try:
        addrinfos = socket.getaddrinfo(hostname, parsed.port or 443, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise SSRFError(f"DNS resolution failed for '{hostname}': {exc}") from exc

    if not addrinfos:
        raise SSRFError(f"No DNS results for '{hostname}'")

    for family, _type, _proto, _canonname, sockaddr in addrinfos:
        ip_str = sockaddr[0]
        if _is_blocked_ip(ip_str):
            raise SSRFError(
                f"URL resolves to blocked IP {ip_str} (hostname: {hostname})"
            )

    return url


def validate_hostname(
    hostname: str,
    port: int = 22,
    *,
    allow_private: bool = False,
) -> str:
    """Validate a hostname + port for non-HTTP protocols (e.g. SFTP).

    Args:
        hostname: The hostname or IP to validate.
        port: The target port.
        allow_private: If True, skip IP-range checks.

    Returns:
        The validated hostname.

    Raises:
        SSRFError: If the hostname resolves to a blocked IP.
    """
    if not hostname or not hostname.strip():
        raise SSRFError("Empty hostname")

    if allow_private:
        return hostname

    # Check if hostname is already a literal IP
    try:
        if _is_blocked_ip(hostname):
            raise SSRFError(f"Blocked IP address: {hostname}")
        return hostname
    except ValueError:
        pass  # Not a literal IP — resolve via DNS

    try:
        addrinfos = socket.getaddrinfo(hostname, port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise SSRFError(f"DNS resolution failed for '{hostname}': {exc}") from exc

    if not addrinfos:
        raise SSRFError(f"No DNS results for '{hostname}'")

    for _family, _type, _proto, _canonname, sockaddr in addrinfos:
        ip_str = sockaddr[0]
        if _is_blocked_ip(ip_str):
            raise SSRFError(
                f"Hostname resolves to blocked IP {ip_str} (hostname: {hostname})"
            )

    return hostname
