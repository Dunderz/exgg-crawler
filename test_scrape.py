import os
from supabase import create_client
from playwright.sync_api import sync_playwright
from datetime import datetime
from dotenv import load_dotenv
from stealth import launch_stealth_browser

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

CFN_ID = os.getenv("CFN_ID")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def login_and_fetch():
    with sync_playwright() as p:
        # browser = p.chromium.launch(headless=True)
        # context = browser.new_context(storage_state="cfn_auth.json")

        # Launch stealth browser
        browser, context = launch_stealth_browser(p)

        # Load your saved CFN login session (very important)
        context = browser.new_context(
            storage_state="cfn_auth.json",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/121.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            locale="en-US",
            timezone_id="America/New_York",
        )

        # Re-inject stealth patches into new context
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

        context.add_init_script("""
            Object.defineProperty(navigator, 'plugins', {
                get: () => [1, 2, 3, 4]
            });
        """)

        context.add_init_script("""
            Object.defineProperty(navigator, 'languages', {
                get: () => ['en-US', 'en']
            });
        """)
        
        page = context.new_page()

        page.goto("https://www.streetfighter.com/6/buckler/ranking/master")
        page.wait_for_load_state("networkidle")
        print("Currently at:", page.url)

        ul = page.locator("ul[class^='ranking_ranking_list']")
        player_ul = ul.nth(1)

        rows = player_ul.locator("li").all()

        for row in rows:
            name = row.locator("span[class^='ranking_name']").inner_text()
            print(name)

        browser.close()


def save_to_supabase(html_data):
    data = {
        "created_at": datetime.utcnow().isoformat(),
        "data": html_data
    }

    res = supabase.table("cfn_test").insert(data).execute()
    print("Saved to Supabase:", res)


if __name__ == "__main__":
    print("[*] Logging into CFN and scraping your profile...")
    login_and_fetch()

    # print("[*] Uploading to Supabase...")
    # save_to_supabase(html)

    print("Done!")
