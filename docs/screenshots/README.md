# Screenshots

Generated from this repository, not edited by hand. They show the unmodified
sample content so a reader can judge the template rather than someone's
filled-in site.

| File | What it is |
|---|---|
| `hero.png` | The README banner. One continuous page inside a window: light above the seam, dark below it. |
| `home-light.png` | Full homepage, light appearance |
| `home-dark.png` | Full homepage, dark appearance |
| `hero.template.html` | The hero's actual source. Edit this to change the design. |
| `hero.html` | Generated from the template on each run. Not edited by hand. |
| `capture.py` | Regenerates everything above. |

## How the hero is built

It is not a crop. `hero.template.html` is rendered in the same browser, so the
type, the shadows and the rounded corners are real rather than composited.

The window shows one page with a **horizontal** seam. Horizontal, because a page
has generous gutters between sections and almost none between words: a vertical
seam cuts through text and reads as a rendering fault.

`capture.py` measures both captures, finds every gap between sections, and puts
the seam and the bottom edge at the **centre** of one. The centre is the point —
an edge parked at the end of a gap sits closer to one paragraph than the other
and reads as misaligned, while the midpoint reads as deliberate. Wider gaps are
preferred over merely nearer ones, because a 22px gap leaves 11px of air on each
side and a 7px gap looks like the line is touching the text. Change the sample
content and the numbers move with it.

The banner carries its own near-black ground and a hairline frame, so it reads
the same on GitHub's light and dark themes and still has a visible edge on dark.

## Capture settings

| Setting | Value |
|---|---|
| Browser | Chromium via Playwright |
| Page viewport | 1440 x 960 CSS px, full page |
| Hero viewport | 1200 x 560 CSS px |
| `deviceScaleFactor` | 2 — `hero.png` is 2400 x 1120, sharp at the width GitHub renders |
| Appearance | `prefers-color-scheme` set per capture; no `localStorage` theme is written |

## Regenerating

```bash
pip install playwright pillow numpy
playwright install chromium
python docs/screenshots/capture.py
```

The script serves the repository root on port 8899, because the template loads
its shared navigation and footer with `fetch`, which does not work from
`file://`.

### Fonts

The CSS asks for the Apple system stack. On a machine that does not have it,
install [Inter](https://rsms.me/inter/) and alias the stack to it — Inter is the
closest widely available match to SF Pro. Without the alias the captures fall
back to DejaVu Sans and misrepresent the typography.

```xml
<!-- /etc/fonts/conf.d/99-apple-alias.conf -->
<match target="pattern"><test name="family"><string>-apple-system</string></test>
  <edit name="family" mode="assign" binding="strong"><string>Inter</string></edit></match>
<match target="pattern"><test name="family"><string>SF Pro Text</string></test>
  <edit name="family" mode="assign" binding="strong"><string>Inter</string></edit></match>
```

Regenerate after any change to layout, typography, colour or the sample content,
and commit the new images in the same commit as the change that caused them.
