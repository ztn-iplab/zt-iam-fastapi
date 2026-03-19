import ipaddress

import requests


def _is_public_ip(value: str | None) -> bool:
    if not value:
        return False
    try:
        ip = ipaddress.ip_address(value)
        return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved)
    except ValueError:
        return False


def get_ip_location(ip):
    if not _is_public_ip(ip):
        return "Unknown"
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json", timeout=0.8)
        if response.status_code == 200:
            data = response.json()
            city = data.get("city")
            country = data.get("country")
            return f"{city}, {country}" if city and country else "Unknown"
    except Exception:
        pass
    return "Unknown"
