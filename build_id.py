import requests
from bs4 import BeautifulSoup
import json

BUCKLER_BASE = "https://www.streetfighter.com/6/buckler/en/"

def fetch_build_id():
    """Fetch the current Next.js build ID from Buckler."""
    html = requests.get(BUCKLER_BASE).text

    # Extract the __NEXT_DATA__ script tag
    soup = BeautifulSoup(html, "html.parser")
    script = soup.find("script", id="__NEXT_DATA__")

    if not script:
        raise RuntimeError("Could not find __NEXT_DATA__ on page.")

    data = json.loads(script.string)

    # Extract the buildId key
    build_id = data.get("buildId")
    if not build_id:
        raise RuntimeError("buildId missing from __NEXT_DATA__ JSON.")

    return build_id


if __name__ == "__main__":
    print("BUILD ID =", fetch_build_id())
