import os
from supabase import create_client
from playwright.sync_api import sync_playwright
from datetime import datetime
from dotenv import load_dotenv

import time

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

CFN_ID = os.getenv("CFN_ID")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def login_and_fetch():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

        # --- Visit CFN page ---
        page = context.new_page()

        print("Opening CFN login page...")
        page.goto("https://www.streetfighter.com/6/buckler/auth/loginep?redirect_url=/")
        
        print("\nLog in manually in the browser window.")
        print("When you're fully logged in and can see your profile, come back here.")
        input("Press ENTER here when done: ")

        # Save session to cfn_auth.json
        context.storage_state(path="cfn_auth.json")
        print("\nSaved session to cfn_auth.json")

        browser.close()


def save_to_supabase(html_data):
    data = {
        "scraped_at": datetime.utcnow().isoformat(),
        "html": html_data
    }

    res = supabase.table("cfn_test").insert(data).execute()
    print("Saved to Supabase:", res)


if __name__ == "__main__":
    print("[*] Logging into CFN and scraping your profile...")
    html = login_and_fetch()

    # print("[*] Uploading to Supabase...")
    # save_to_supabase(html)

    print("Done!")
