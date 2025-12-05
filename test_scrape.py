import os
from supabase import create_client
from playwright.sync_api import sync_playwright
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

CFN_ID = os.getenv("CFN_ID")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def login_and_fetch():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(storage_state="cfn_auth.json")
        
        page = context.new_page()

        page.goto("https://www.streetfighter.com/6/buckler/en")
        page.wait_for_load_state("networkidle")

        print("Currently at:", page.url)

        page.get_by_role("link", name="Profile", exact=True).click()
        page.wait_for_load_state("networkidle")

        html = page.content()

        browser.close()
        return html


def save_to_supabase(html_data):
    data = {
        "created_at": datetime.utcnow().isoformat(),
        "data": html_data
    }

    res = supabase.table("cfn_test").insert(data).execute()
    print("Saved to Supabase:", res)


if __name__ == "__main__":
    print("[*] Logging into CFN and scraping your profile...")
    html = login_and_fetch()

    print("[*] Uploading to Supabase...")
    save_to_supabase(html)

    print("Done!")
