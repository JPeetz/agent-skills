# Image Optimization Guidelines

## Format Selection

| Format | Best For | Notes |
|--------|----------|-------|
| WebP | Photos, illustrations | 25–35% smaller than JPEG; widely supported |
| AVIF | Photos with fine detail | 50% smaller than JPEG; limited but growing support |
| JPEG | Photographs | Universal fallback |
| PNG | Graphics with transparency, screenshots | Lossless, avoid for photos |
| SVG | Icons, logos, illustrations | Scalable, tiny file sizes |

## Responsive Images with `<picture>`

```html
<picture>
  <source type="image/avif" srcset="photo-800.avif 800w, photo-1200.avif 1200w" sizes="(max-width: 600px) 100vw, 50vw">
  <source type="image/webp" srcset="photo-800.webp 800w, photo-1200.webp 1200w" sizes="(max-width: 600px) 100vw, 50vw">
  <img src="photo-800.jpg" width="800" height="600" alt="Description" loading="lazy" decoding="async">
</picture>
```

## Critical Attributes

| Attribute | Purpose |
|-----------|---------|
| `width` + `height` | Reserve layout space (prevents CLS) |
| `loading="lazy"` | Defer offscreen images (standard for below-fold) |
| `loading="eager"` | Ensure LCP image loads immediately |
| `decoding="async"` | Decode off the main thread |
| `fetchpriority="high"` | Hint for LCP image prioritization |

## Lazy Loading Strategy

- **Above-fold:** Eager load with `loading="eager"`, `fetchpriority="high"`, `width`/`height` set
- **Below-fold:** `loading="lazy"` with a 200px threshold (browser default)
- **Avoid:** Over-lazy-loading the hero image or LCP candidate — it delays LCP

## Tooling

- `squoosh` (CLI / web) — manual compression
- `sharp` (Node.js) — programmatic resize + format conversion
- `imagemagick` — batch resizing
- Cloudinary / imgix — CDN-based image transformation