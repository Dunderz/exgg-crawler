import os
import asyncio
from supabase import create_client
from playwright.async_api import async_playwright
from datetime import datetime
from dotenv import load_dotenv
from stealth import launch_stealth_browser
from build_id import fetch_build_id

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
BUCKLER_BASE = "https://www.streetfighter.com/6/buckler"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)



async def create_stealth_context(p):
    # Launch stealth browser
    browser, _ = await launch_stealth_browser(p)

    # Load your saved CFN login session (very important)
    context = await browser.new_context(
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
    await context.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")
    await context.add_init_script("Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4] });")
    await context.add_init_script("Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });")

    return browser, context



async def scrape_leaderboard_page(page, page_number: int, build_id: str):
    url = f"https://www.streetfighter.com/6/buckler/_next/data/{build_id}/en/ranking/master.json?page={page_number}&season_type=1"
    
    response = await page.request.get(url)
    
    if response.status != 200:
        raise RuntimeError(f"Bad status {response.status} for {url}")
    
    data = await response.json()
    raw_players = data['pageProps']['master_rating_ranking']['ranking_fighter_list']
    
    seen = set()
    players = []

    for raw_player in raw_players:
        personal_info = raw_player['fighter_banner_info']['personal_info']
        
        player_id = personal_info['short_id']
        player_name = personal_info['fighter_id']
        player_mr = raw_player['rating']
        player_character = raw_player['character_name']
        
        player = {
            "player_name": player_name,
            "player_mr": player_mr,
            "player_id": player_id,
            "player_character": player_character,
            "created_at": datetime.utcnow().isoformat()
        }

        if player_id not in seen:
            seen.add(player_id)
            players.append(player)

    return players




async def fetch_page_with_limit(page, page_number: int, build_id: str, semaphore: asyncio.Semaphore):
    async with semaphore:
        players = await scrape_leaderboard_page(page, page_number, build_id)
        return page_number, players
    
    
    
    
async def paginate_leaderboard(page):
    build_id = fetch_build_id(BUCKLER_BASE)
    semaphore = asyncio.Semaphore(5)
    tasks = []
    
    for page_number in range(1, 10):
        tasks.append(asyncio.create_task(fetch_page_with_limit(page, page_number, build_id, semaphore)))

    results = await asyncio.gather(*tasks)
    
    for page_number, players in sorted(results, key=lambda x: x[0]):
        if not players:
            print(f"Reached end of leaderboard at page {page_number}.")
            continue
        
        print(f"[*] Uploading page {page_number} to Supabase...")
        save_to_supabase(players)





async def login_and_fetch():
    async with async_playwright() as p:
        
        browser, context = await create_stealth_context(p)
        page = await context.new_page()

        #Scrape ranked leaderboard
        await paginate_leaderboard(page)
        await browser.close()




def save_to_supabase(players):
    supabase.table('players').insert(players).execute()




if __name__ == "__main__":
    print("[*] Logging into CFN and scraping player data...")
    asyncio.run(login_and_fetch())

    print("Done!")
