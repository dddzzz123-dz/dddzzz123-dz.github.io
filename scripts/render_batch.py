"""Capture actual HTML outputs with a shared local browser."""
import asyncio
import json
from pathlib import Path
from PIL import Image
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"


async def main():
    batch = json.loads((SITE / "data/batch.json").read_text(encoding="utf-8"))
    records = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        semaphore = asyncio.Semaphore(3)
        async def capture(sample_id):
            async with semaphore:
                page = await browser.new_page(viewport={"width": 1160, "height": 1500}, device_scale_factor=1.5)
                await page.goto((SITE / "samples/html" / f"{sample_id}.html").as_uri(), wait_until="load")
                await page.evaluate("document.fonts.ready")
                paper = page.locator(".paper")
                metrics = await page.evaluate("""() => ({
                    width: document.querySelector('.paper').getBoundingClientRect().width,
                    height: document.querySelector('.paper').getBoundingClientRect().height,
                    units: document.querySelectorAll('.reason-step').length,
                    min_visual_width: Math.min(...Array.from(document.querySelectorAll('.reason-step svg'), e => e.getBoundingClientRect().width)),
                    overflowing_text: Array.from(document.querySelectorAll('.reason-step p,.step-heading h2')).filter(e => e.scrollWidth > e.clientWidth + 1).length
                })""")
                assert metrics["overflowing_text"] == 0, (sample_id, metrics)
                out = SITE / "samples/jpg" / f"{sample_id}.jpg"
                await paper.screenshot(path=str(out), type="jpeg", quality=90)
                if "baseline" not in sample_id:
                    with Image.open(out) as image:
                        image.thumbnail((480, 900))
                        image.save(SITE / "samples/thumbs" / f"{sample_id}.webp", quality=83, method=6)
                records.append({"id": sample_id, **metrics})
                print(f"Rendered {sample_id}: {int(metrics['width'])} x {int(metrics['height'])}", flush=True)
                await page.close()
        await asyncio.gather(*(capture(s["id"]) for s in batch["samples"]), capture("EX-017-baseline"))
        await browser.close()
    lookup = {r["id"]: r for r in records}
    report = {
        "batch_id": batch["id"], "rendered": len(batch["samples"]), "screenshots": len(records),
        "scope": "Actual Chromium HTML screenshots; text container overflow checked at export width.",
        "comparison": {"kind": "controlled_reproduction", "sample": "EX-017", "before": lookup["EX-017-baseline"], "after": lookup["EX-017"]},
        "outputs": sorted(records, key=lambda r: r["id"])
    }
    assert report["comparison"]["after"]["min_visual_width"] > report["comparison"]["before"]["min_visual_width"]
    (SITE / "data/render-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (SITE / "data/render-report.js").write_text("window.DEMO_RENDER_REPORT=" + json.dumps(report, ensure_ascii=False) + ";", encoding="utf-8")
    print("All actual screenshots and thumbnails saved.", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
