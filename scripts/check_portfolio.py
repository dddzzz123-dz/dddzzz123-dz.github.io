import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
QA = ROOT / "qa"

async def main():
    QA.mkdir(exist_ok=True)
    report = {"viewports": [], "links": [], "errors": []}
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for width, height, label in [(1440, 1000, "desktop"), (390, 844, "mobile"), (320, 780, "small")]:
            page = await browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            page_errors = []
            page.on("pageerror", lambda e: page_errors.append(str(e)))
            await page.goto("http://127.0.0.1:4173/", wait_until="networkidle")
            metrics = await page.evaluate("""() => ({
              scrollWidth: document.documentElement.scrollWidth,
              viewport: innerWidth,
              web: document.querySelectorAll('.web-item').length,
              skills: document.querySelectorAll('.skill-item').length,
              plugins: document.querySelectorAll('.plugin-item').length,
              broken: [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.src)
            })""")
            assert metrics["scrollWidth"] <= width + 1, (label, metrics)
            assert metrics["web"] == 2 and metrics["skills"] == 2 and metrics["plugins"] == 5, metrics
            assert not metrics["broken"], metrics
            assert not page_errors, page_errors
            await page.screenshot(path=str(QA / f"github-entry-{label}.png"), full_page=True)
            report["viewports"].append({"label": label, **metrics, "no_horizontal_overflow": True})
            live_link = page.locator('a[href="https://dddzzz123-dz.github.io/luohu-rental-map/"]')
            assert await live_link.get_attribute("target") == "_blank"
            assert await live_link.get_attribute("rel") == "noopener"
            await page.close()
        page = await browser.new_page(viewport={"width": 1200, "height": 900})
        await page.goto("http://127.0.0.1:4173/", wait_until="networkidle")
        resume_link = page.locator('a[href="assets/daiying-resume.pdf"]').first
        assert await resume_link.get_attribute("download") == ""
        assert await resume_link.get_attribute("href") == "assets/daiying-resume.pdf"
        assert await page.locator('.skill-item').count() == 2
        assert await page.locator('.copy-button').count() == 2
        assert await page.locator('.plugin-item').count() == 5
        assert await page.locator('.web-preview img').count() == 3
        assert await page.locator('a[download][href$="main.zip"]').count() == 6
        await page.locator('a[href="#collection-plugins"]').click()
        await page.wait_for_timeout(220)
        assert "is-highlighted" in (await page.locator('.plugin-project').get_attribute('class'))
        await page.close()
        await browser.close()
    (QA / "github-entry-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
