# Brand

Showcase images for Astra.

## No site logo

The template renders no logo in the navigation and none in the footer. A
template that ships a mark makes every user either adopt someone else's brand or
delete it, so it ships none; add your own if you want one, and nothing here
fights you for the space.

The Education and Experience entries **do** keep their institution logo slot —
that image is the user's own institution, not the template's brand.
`assets/images/institution.svg` is the neutral placeholder that stands in until
it is replaced.

## Showcase images

| File | Size | Use |
|---|---|---|
| `showcase-social.png` | 1280 x 640 | GitHub → Settings → Social preview. Also the Open Graph image. |
| `showcase.png` | 1280 x 720 | 16:9 slots — a project card on a personal site, a slide, a post. |

Both carry their own near-black ground and a hairline frame, so they read the
same on a light and a dark page and still have a visible edge on GitHub's dark
theme. The name is set as type. Neither image depends on an external font or on
transparency.

## Regenerating

The showcase images are built from the same captures as the README hero, so
regenerate the screenshots first:

```bash
python docs/screenshots/capture.py
```
