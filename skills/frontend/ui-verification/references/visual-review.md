# Visual review

Comparing before and after captures. A screenshot is evidence, not a verdict —
this guide is about producing evidence a reviewer can trust, and about the
comparison mistakes that manufacture regressions and hide real ones.

## Make the pair comparable

A before/after pair that differs on any axis other than the change is not a
pair. Match all of these, and record them next to the images:

| Axis | Requirement |
|---|---|
| Viewport | Identical width and height; device scale factor identical |
| Theme | Same resolved theme — assert the attribute, do not assume the toggle worked |
| Locale and direction | Same `lang`/`dir`; strings identical unless the change touched copy |
| Fonts | Wait for `document.fonts.ready`; a fallback-font capture shifts every line |
| Scroll position | Same anchor; a sticky header read at a different offset looks like a spacing bug |
| Data | Same seed and same fixture; one extra row changes every measurement below it |
| Motion | `prefers-reduced-motion: reduce` for stills, so animations are not caught mid-transition |
| Zoom | 100%; no browser zoom, no OS scaling differences |

Capture full-page and viewport-sized versions. Full-page catches reflow far down
the page; viewport-sized catches the thing the user actually sees above the fold.

## Inspect, in this order

1. **Layout skeleton first.** Ignore colour and type. Do the blocks sit in the
   same places? A shift of 1–2px is usually subpixel noise; a shift that moves a
   block by its own line height is a change.
2. **Then spacing.** Compare gaps between sections against each other, not
   against memory. An asymmetric gap that appears on only one side of the change
   is usually an accidental margin.
3. **Then type.** Size, weight, line height, and wrapping. A line that now wraps
   where it did not is a width change, not a font change — check the container.
4. **Then colour and contrast.** Prefer the computed values from the `axe-scan`
   probe over eyeballed pixels; screenshots compress and colour-manage.
5. **Then state.** Is the after-capture showing the same state as the
   before-capture? A hover, a focus ring, or a toast caught in one frame reads
   as a styling regression.

## Suspicious duplicates

A pair that looks *too* similar deserves scrutiny as much as one that differs:

- **Byte-identical images** across a code change that touched layout strongly
  suggest a stale build, a cached page, or a capture taken before the change
  landed. Re-run the capture against a fresh server.
- **The same element in the same position but with different rendering** can
  mean the screenshot tool's font loading differed, not that the app changed.
- **Two supposedly different themes rendering identically** is the classic
  attribute-theming failure: the toggle did nothing and both captures are light
  mode. Verify the resolved theme, not the toggle's visual state.
- **Identical crops with different file sizes** usually trace to metadata or
  compression settings, not pixels. Compare decoded pixels, not bytes.

## Separating observation from measurement

Write two distinct lists. They get merged only in the final report, and each
line keeps its provenance:

```text
visual observations (from crops):
- primary button appears 4px narrower after the change; label unchanged
- card corner radius looks larger, top-left only

measured (from probes):
- target-size: 96x40px before, 92x40px after, 360px width, dark
- axe contrast: unchanged, 5.1:1 on the primary button label in both
```

An observation that a probe can decide should become a measurement before it is
reported. "Looks cramped" is the inference this workflow replaces with a gap
value.

## Reviewing someone else's screenshots

You often get images with no harness and no context. Then:

- Ask for the conditions if they are not stated; missing viewport and theme make
  the pair uninterpretable.
- Compare at native resolution, never a scaled preview. Downscaling hides 1px
  borders and focus rings.
- Crop to the region of interest and compare side by side at the same scale
  before drawing a conclusion about a small element.
- Treat an annotated screenshot (arrows, circles) as a claim to verify, not as
  evidence. Verify the underlying state before agreeing with the annotation.
- Say what you could not determine. "No diff visible in the supplied crop;
  header not included in either image" is a useful review; a confident "looks
  fine" over a partial crop is not.

## When a diff is intentional

Not every difference is a regression. Before reporting, check whether the change
was the point of the fix: a control that grew from 32px to 44px, a label that
re-wrapped because the copy changed, a spacing increase that was the requested
outcome. Report those as `expected` with the reason, so the next reviewer does
not re-open them.

## Reporting

- Artifact paths for both images, named `before-` and `after-` with route,
  viewport, and theme: `before-checkout-360-dark.png`.
- Never overwrite a before-artifact with an after-capture. The pair is the
  evidence; a lone "after" image proves nothing.
- State the conditions next to the images, not in a separate document.
- Keep visual observations labelled as such; the verdict rests on measurements.
