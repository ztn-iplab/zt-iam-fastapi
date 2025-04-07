import requests

def get_ip_location(ip):
    try:
        response = requests.get(f"https://ipinfo.io/{ip}/json")
        if response.status_code == 200:
            data = response.json()
            city = data.get("city")
            country = data.get("country")
            return f"{city}, {country}" if city and country else "Unknown"
    except:
        pass
    return "Unknown"
