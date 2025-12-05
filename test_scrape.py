import os
from supabase import create_client
from playwright.sync_api import sync_playwright
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def login_and_fetch():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # --- Go to CFN login page ---
        page = context.new_page()
        page.goto("https://www.streetfighter.com/6/buckler/login")

        # --- Fill login form ---
        page.fill("input[name='username']", os.getenv("CFN_USERNAME"))
        page.fill("input[name='password']", os.getenv("CFN_PASSWORD"))
        page.click("button[type='submit']")

        page.wait_for_load_state("networkidle")

        # --- Go to your profile page ---
        page.goto("https://www.streetfighter.com/6/buckler/profile")
        page.wait_for_load_state("networkidle")

        html = page.content()

        browser.close()
        return html


def save_to_supabase(html_data):
    data = {
        "scraped_at": datetime.utcnow().isoformat(),
        "html": html_data
    }

    res = supabase.table("crawler_test").insert(data).execute()
    print("Saved to Supabase:", res)


if __name__ == "__main__":
    print("[*] Logging into CFN and scraping your profile...")
    html = login_and_fetch()

    print("[*] Uploading to Supabase...")
    save_to_supabase(html)

    print("Done!")
