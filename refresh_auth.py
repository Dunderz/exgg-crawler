"""
refresh_cfn_session.py
----------------------

Use this script to manually refresh your CFN authentication.
It opens a visible browser, you log in manually, and saves the
session cookies + tokens into `cfn_auth.json`.

Run this once every few weeks/months when your CFN session expires.
"""

from playwright.sync_api import sync_playwright

def refresh_cfn_session():
    with sync_playwright() as p:
        print("Launching browser...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()  # fresh, empty profile
        page = context.new_page()

        print("\nOpening CFN login page...\n")
        page.goto("https://www.streetfighter.com/6/buckler/auth/loginep?redirect_url=/")

        print("--------------------------------------------------------")
        print("  Log in manually in the browser window that opened.    ")
        print("  Use your CFN username & password as usual.            ")
        print("                                                        ")
        print("  Once you see your Profile page loaded, come back here ")
        print("  and press ENTER to save your session.                 ")
        print("--------------------------------------------------------\n")

        input("Press ENTER after you are fully logged in: ")

        # Save cookies / localStorage / session state
        context.storage_state(path="cfn_auth.json")
        print("\n✅ Saved session to cfn_auth.json")

        browser.close()
        print("Browser closed. Authentication refresh complete.\n")

if __name__ == "__main__":
    refresh_cfn_session()
