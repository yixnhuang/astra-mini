#!/usr/bin/env python3
"""Regenerate the README images for this template.

Serves the repository root over HTTP, loads the homepage in Chromium under both
colour-scheme preferences, and writes:

    docs/screenshots/home-light.png   full homepage, light appearance
    docs/screenshots/home-dark.png    full homepage, dark appearance
    docs/screenshots/hero.png         the README banner, composed from both

The hero is not a crop. It is `hero.template.html` rendered in the same browser:
one continuous page inside a window, light above a horizontal seam and dark
below it. The seam position and the window height are chosen by measuring the
captures: both are placed at the *centre* of a gap between sections, so the seam
sits the same distance from the paragraph above it as from the paragraph below,
and the bottom edge cuts the page in a gap rather than through a line. Change
the template to change the design; the numbers look after themselves.

Requirements:

    pip install playwright pillow numpy
    playwright install chromium

Run from anywhere:

    python docs/screenshots/capture.py

Fonts: the template's CSS asks for the Apple system stack. On a machine without
it, install Inter and alias it — Inter is the closest widely available match to
SF Pro, and without an alias the captures fall back to DejaVu Sans and
misrepresent the typography.
"""

from __future__ import annotations

import asyncio
import functools
import http.server
import socketserver
import threading
from pathlib import Path

import numpy as np
from PIL import Image
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "screenshots"
PORT = 8899

# Page capture
VIEWPORT = {"width": 1440, "height": 960}
SCALE = 2                      # deviceScaleFactor

# Hero composition — must match hero.template.html
HERO_VIEWPORT = {"width": 1200, "height": 560}
WIN_W = 660                    # window width in the hero, CSS px
WIN_H_RANGE = (398, 442)       # design height is ~420, nudged for a clean bottom
PAGE_CSS_W = 1440              # capture viewport width
SEAM_TARGET, SEAM_LO, SEAM_HI = 0.55, 0.34, 0.74
INK_THRESHOLD = 0.4          # a row this uniform is background, not content
MIN_GUTTER = 6               # window px; shorter blank runs are line spacing
WIDTH_BONUS = 1.5            # how far it is worth travelling for a roomier gap
ZOOM = WIN_W / PAGE_CSS_W

# Per-repository copy for the hero. Edit these, not the rendered PNG.
HERO_TITLE = "Astra Mini"
HERO_LEDE = (
    "The single-page edition. One academic homepage, no framework and no build step."
)
HERO_META = "1 page <i>/</i> Automatic light &amp; dark <i>/</i> MIT"


def serve(directory: Path, port: int):
    handler = functools.partial(
        http.server.SimpleHTTPRequestHandler, directory=str(directory)
    )

    class Server(socketserver.TCPServer):
        allow_reuse_address = True

    httpd = Server(("127.0.0.1", port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def _ink_rows(pixels: np.ndarray, height: int) -> np.ndarray:
    """One flag per window row: True where the captured page has content there.

    A row of the page is blank when every pixel across it is the background
    colour, so its standard deviation is essentially zero.
    """
    rows = np.empty(height + 1, dtype=bool)
    for y in range(height + 1):
        px = int(y / ZOOM * SCALE)
        band = pixels[max(0, px - 1):px + 2]
        rows[y] = band.size == 0 or band.std() > INK_THRESHOLD
    return rows


def _gutters(ink: np.ndarray, min_length: int = MIN_GUTTER) -> list[tuple[int, int]]:
    """Maximal runs of blank window rows, as [start, end) pairs."""
    runs, start = [], None
    for y, inked in enumerate(ink):
        if not inked and start is None:
            start = y
        elif inked and start is not None:
            if y - start >= min_length:
                runs.append((start, y))
            start = None
    if start is not None and len(ink) - start >= min_length:
        runs.append((start, len(ink)))
    return runs


def _pick_gutter_centre(gutters, target, lo, hi):
    """Centre of the best gutter near `target`, or None if none is in range.

    The centre matters, not merely a blank row: an edge parked at the end of a
    gap sits closer to one paragraph than the other and reads as misaligned.
    Halfway between the text above and the text below reads as deliberate.

    Width matters too. A 22px gap gives an edge 11px of air on each side; a 7px
    gap gives 3px and looks like the line is touching the text. So a roomier gap
    is worth travelling for, which is what WIDTH_BONUS buys.
    """
    usable = [(a, b) for a, b in gutters if lo <= (a + b) / 2 <= hi]
    if not usable:
        return None
    a, b = min(
        usable,
        key=lambda r: abs((r[0] + r[1]) / 2 - target) - WIDTH_BONUS * (r[1] - r[0]),
    )
    return round((a + b) / 2)


def plan_window() -> tuple[int, int]:
    """Choose the hero window height and the seam position.

    Two edges have to land in the page's own whitespace: the seam, where the
    light capture meets the dark one, and the bottom of the window, where the
    page is cut off. Both are placed at the *centre* of a gutter, so the seam is
    equidistant from the paragraph above and the paragraph below.

    The window always starts at the top of the page — that edge is already
    clean, and cropping into the header just looks broken.
    """
    light = np.asarray(Image.open(OUT / "home-light.png").convert("L")).astype(np.float32)
    dark = np.asarray(Image.open(OUT / "home-dark.png").convert("L")).astype(np.float32)

    lo_h, hi_h = WIN_H_RANGE
    nominal = (lo_h + hi_h) / 2

    # A row counts as blank only if it is blank in both captures, so the seam
    # works for the light page above it and the dark page below it.
    ink = _ink_rows(light, hi_h) | _ink_rows(dark, hi_h)
    gutters = _gutters(ink)

    height = _pick_gutter_centre(gutters, nominal, lo_h, hi_h) or round(nominal)
    seam = _pick_gutter_centre(
        gutters, height * SEAM_TARGET, height * SEAM_LO, height * SEAM_HI
    ) or round(height * SEAM_TARGET)
    return height, seam


def write_hero_html(height: int, seam: int) -> None:
    template = (OUT / "hero.template.html").read_text(encoding="utf-8")
    html = (
        template.replace("__TITLE__", HERO_TITLE)
        .replace("__LEDE__", HERO_LEDE)
        .replace("__META__", HERO_META)
        .replace("__WINH__", str(height))
        .replace("__SEAM__", str(seam))
    )
    (OUT / "hero.html").write_text(html, encoding="utf-8")


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # The template loads its navigation and footer with fetch, which does not
    # work from file://, so everything is served over HTTP.
    httpd = serve(ROOT, PORT)
    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch()

            for scheme in ("light", "dark"):
                context = await browser.new_context(
                    viewport=VIEWPORT, device_scale_factor=SCALE, color_scheme=scheme
                )
                page = await context.new_page()
                await page.goto(f"http://127.0.0.1:{PORT}/", wait_until="networkidle")
                await page.wait_for_timeout(700)
                await page.screenshot(path=OUT / f"home-{scheme}.png", full_page=True)
                await context.close()
                print("wrote", OUT / f"home-{scheme}.png")

            height, seam = plan_window()
            write_hero_html(height, seam)
            print(f"hero window {WIN_W}x{height}, seam at {seam}")

            context = await browser.new_context(
                viewport=HERO_VIEWPORT, device_scale_factor=SCALE
            )
            page = await context.new_page()
            await page.goto(
                f"http://127.0.0.1:{PORT}/docs/screenshots/hero.html",
                wait_until="networkidle",
            )
            await page.wait_for_timeout(500)
            await page.screenshot(path=OUT / "hero.png")
            await context.close()
            print("wrote", OUT / "hero.png")

            await browser.close()
    finally:
        httpd.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
