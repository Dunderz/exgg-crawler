import os
from supabase import create_client
from playwright.sync_api import sync_playwright
from datetime import datetime
from dotenv import load_dotenv
from stealth import launch_stealth_browser
from build_id import fetch_build_id

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
BUCKLER_BASE = "https://www.streetfighter.com/6/buckler"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)



def create_stealth_context(p):
    # Launch stealth browser
    browser, _ = launch_stealth_browser(p)

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

    # stealth patches
    context.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")
    context.add_init_script("Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4] });")
    context.add_init_script("Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });")

    return browser, context



def scrape_leaderboard_page(page, page_number: int):
    build_id = fetch_build_id(BUCKLER_BASE)
    url = f"https://www.streetfighter.com/6/buckler/_next/data/{build_id}/en/ranking/master.json?page={page_number}&season_type=1"

    response = page.request.get(url)
    
    if response.status != 200:
        raise RuntimeError(f"Bad status {response.status} for {url}")
    
    data = response.json()
    raw_players = data['pageProps']['master_rating_ranking']['ranking_fighter_list']
    
    players = []

    for raw_player in raw_players:

        player = {
            "player_name": raw_player['fighter_banner_info']['personal_info']['fighter_id'],
            "player_mr": int(raw_player['rating']),
            "player_id": raw_player['fighter_banner_info']['personal_info']['short_id'],
            "created_at": datetime.utcnow().isoformat()
        }

        players.append(player)

    return players




def paginate_leaderboard(page):
    page_number = 1

    while page_number < 20:
        players = scrape_leaderboard_page(page, page_number)

        if not players:
            print("Reached end of leaderboard.")
            break
        
        print(f"[*] Uploading page {page_number} to Supabase...")
        save_to_supabase(players)
        
        page_number += 1




def login_and_fetch():
    with sync_playwright() as p:
        
        browser, context = create_stealth_context(p)
        page = context.new_page()

        #Scrape ranked leaderboard
        paginate_leaderboard(page)
        browser.close()




def save_to_supabase(players):
    supabase.table("players").insert(players).execute()




if __name__ == "__main__":
    print("[*] Logging into CFN and scraping player data...")
    players = login_and_fetch()

    print("Done!")
