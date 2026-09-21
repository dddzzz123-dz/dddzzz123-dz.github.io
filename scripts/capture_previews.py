import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "site" / "assets" / "previews"
PAGES = {
    "cityu-course-board.png": "https://dddzzz123-dz.github.io/cityu-msaib-course-board/",
    "luohu-rental-map.png": "https://dddzzz123-dz.github.io/luohu-rental-map/",
    "beishatan-rental-map.png": "https://dddzzz123-dz.github.io/beishatan-rental-map/",
}

async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for filename, url in PAGES.items():
            page = await browser.new_page(viewport={"width": 1200, "height": 760}, device_scale_factor=1)
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(1800)
                await page.screenshot(path=str(OUT / filename), full_page=False)
                print(f"saved {filename}")
            except Exception as exc:
                print(f"failed {filename}: {exc}")
            finally:
                await page.close()
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
