"""Browser QA for the site, its actual interactions, and export pages."""
import asyncio
import json
import sys
from pathlib import Path
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "qa"
BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:4173"


async def main():
    QA.mkdir(exist_ok=True)
    results, errors, failed = [], [], []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for width, height, label in [(1440, 1000, "desktop"), (390, 844, "mobile"), (320, 780, "small"), (768, 1024, "tablet")]:
            page = await browser.new_page(viewport={"width": width, "height": height}, device_scale_factor=1)
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("response", lambda r: failed.append({"status": r.status, "url": r.url}) if r.status >= 400 else None)
            for route in ["index.html", "case.html"]:
                await page.goto(BASE.rstrip("/") + "/" + route, wait_until="networkidle")
                await page.emulate_media(reduced_motion="reduce")
                await page.evaluate("document.fonts.ready")
                dimensions = await page.evaluate("""() => ({
                    viewport: innerWidth, width: document.documentElement.scrollWidth,
                    broken_images: [...document.images].filter(i => i.complete && i.naturalWidth === 0).map(i => i.getAttribute('src'))
                })""")
                assert dimensions["width"] <= width + 1, (label, route, dimensions)
                assert not dimensions["broken_images"], (label, route, dimensions)
                if label in ["desktop", "mobile"]:
                    await page.screenshot(path=str(QA / f"{route.split('.')[0]}-{label}.png"), full_page=True)
                    if route == "index.html":
                        await page.screenshot(path=str(QA / f"home-{label}-viewport.png"))
                results.append({"viewport": label, "route": route, "no_horizontal_overflow": True, "loaded_images": True})
                if route == "case.html":
                    assert await page.locator(".sample-card").count() == 24
                    for family in ["single", "parallel", "sequence"]:
                        await page.locator(f'[data-filter="{family}"]').click()
                        assert await page.locator(".sample-card").count() == 8
                    await page.locator('[data-filter="all"]').click()
                    await page.locator('[data-sample="EX-017"]').click()
                    assert await page.locator("#sample-select").input_value() == "EX-017"
                    assert await page.locator("#step-tabs [role=tab]").count() == 6
                    await page.locator('#step-tab-1').click()
                    await page.locator('#step-tab-1').press("End")
                    assert await page.locator('#step-tab-5').get_attribute("aria-selected") == "true"
                    assert "出口" in await page.locator("#result-title").inner_text()
                    assert "EX-017-step-6" in await page.locator("#result-visual img").get_attribute("src")
                    await page.locator('[data-field="visual"]').first.click()
                    assert "highlighted" in await page.locator("#result-visual").get_attribute("class")
                    assert await page.locator("#download-jpg").get_attribute("href") == "samples/jpg/EX-017.jpg"
                    if label == "desktop":
                        await page.locator(".mapping-grid").screenshot(path=str(QA / "mapping-desktop.png"))
                    await page.locator('[data-layout="before"]').click()
                    assert "baseline" in await page.locator("#comparison-image").get_attribute("src")
                    await page.locator('[data-layout="after"]').click()
                    assert "baseline" not in await page.locator("#comparison-image").get_attribute("src")
                    # All 24 samples can be selected and their last frame loads.
                    if label == "desktop":
                        for number in range(1, 25):
                            sample_id = f"EX-{number:03}"
                            await page.locator("#sample-select").select_option(sample_id)
                            tabs = page.locator("#step-tabs [role=tab]")
                            await tabs.last.click()
                            await page.wait_for_function("document.querySelector('#result-visual img').complete && document.querySelector('#result-visual img').naturalWidth > 0")
            await page.close()
        # Relative paths must also work under a GitHub project subdirectory.
        # Direct file opening is independently supported for the delivered copy.
        page = await browser.new_page(viewport={"width": 1200, "height": 900})
        page.on("pageerror", lambda e: errors.append(str(e)))
        await page.goto((ROOT / "site/case.html").as_uri(), wait_until="load")
        assert await page.locator(".sample-card").count() == 24
        await page.locator("#sample-select").select_option("EX-024")
        assert "EX-024" in await page.locator("#sample-details").inner_text()
        await page.close()
        # Exported HTML retains readable flow on mobile.
        page = await browser.new_page(viewport={"width": 390, "height": 844})
        for sample_id in ["EX-001", "EX-017"]:
            await page.goto(BASE.rstrip("/") + "/samples/html/" + sample_id + ".html", wait_until="networkidle")
            assert await page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
        await page.close()
        await browser.close()
    assert not errors, errors
    assert not failed, failed
    report = {"routes_and_viewports": results, "all_sample_controls": 24, "keyboard_tabs": True,
              "field_highlighting": True, "layout_switch": True, "direct_file_preview": True,
              "mobile_exports": True, "javascript_errors": errors, "http_errors": failed}
    (QA / "browser-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
