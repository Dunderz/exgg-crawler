import requests
from bs4 import BeautifulSoup
import json




def load_cookies():
    """Load cookies from Playwright's saved session.json"""
    session = requests.Session()

    with open("cfn_auth.json", "r") as f:
        storage = json.load(f)

    for cookie in storage.get("cookies", []):
        session.cookies.set(
            cookie["name"],
            cookie["value"],
            domain=cookie.get("domain")
        )

    return session




def fetch_build_id(url):
    """Fetch the current Next.js build ID from Buckler using logged-in cookies."""
    session = load_cookies()

    # Very important! CloudFront needs real headers:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "text/html,application/xhtml+xml",
    }

    html = session.get(url, headers=headers).text
    
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
    
