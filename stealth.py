from playwright.async_api import Browser, BrowserContext

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0.0.0 Safari/537.36"
)

async def create_stealth_context(p, storage_state: str = "cfn_auth.json") -> tuple[Browser, BrowserContext]:
    browser = await p.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-infobars",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--window-size=1280,800",
        ],
    )

    context = await browser.new_context(
        storage_state=storage_state,
        user_agent=UA,
        viewport={"width": 1280, "height": 800},
        locale="en-US",
        timezone_id="America/New_York",
    )

    await context.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")
    await context.add_init_script("Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4] });")
    await context.add_init_script("Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });")

    return browser, context
