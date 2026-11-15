# FLAMSA homepage: Lovable motion design

The Home view uses the supplied Lovable JPEG and reproduces the supplied screenshot's dark full-page chamber background, oversized white headline with an orange-to-gold phrase, blue glass borders, full-width interactive chamber, orange numbered points and rising embers. Copy stays in English to match the existing workspace. The context panel follows the image, matching the supplied wide scene screenshot rather than shrinking the scene beside a sidebar.

Current product copy is reviewed in [the Home content audit](home-content-audit.md). Home now describes the implemented archive-wide scenario ranking and cited explanations, filtered CSV export and source inspection, with direct access to Fire behavior. Its scientific/review limitations remain visible; the copy no longer describes ranking as unimplemented.

## Reference and motion

The supplied React route renders an `img` with CSS `kenburns` animation, not a video. `vitest.config.ts` and `setup.ts` configure tests. No video was attached. The user confirmed CSS animation is appropriate after this was explained. Home therefore uses the reference's 22-second background zoom, animated grid, 24 rising particles and pulsing points. A subtle blue glow and rotating light layer add motion over the spherical flame without changing the supplied artwork. No scientific recording is represented by these effects.

The foreground image and its points share an animated coordinate system: they move together, keeping their alignment. The image remains at its original aspect ratio. Four 44-pixel buttons support click, touch, keyboard activation and hover selection after a short delay. Selection updates the existing topic state and contextual panel. The native topic selector remains available.

The `Animate scene` toggle pauses background, particles, grid, scene zoom, flame glow and point pulses. CSS also honors `prefers-reduced-motion`. Component event handlers and hover timers are cleaned up on rerender. Registration remains runtime-local for compatibility with AppTest's fresh runtimes.

## Implementation

- `home_style.py`: Home-only CSS and decorative background. Sora and JetBrains Mono match the Lovable fonts, loaded from Google Fonts with local sans-serif/monospace fallbacks when offline. Selectors scope changes to Home so other workspaces retain their existing appearance.
- `research_scene.py`: isolated Custom Components v2 scene, motion layers and validated topic trigger. No React/Bun runtime or frontend dependencies are needed.
- `home_view.py`: introduction followed immediately by the full-width scene, then topic context, existing navigation, real archive counts and workflow cards.

The packaged image is unchanged: `assets/flamsa-hero.jpg`, 1600 × 912 pixels. Its instrument readings and lunar setting remain conceptual artwork. Archive counts and related investigations come from the loaded snapshot. The reference's illustrative ranking scores and LIVE badge are not presented as computed results.

## Validation

Eight existing interface AppTests passed, including homepage navigation, topic synchronization, dataset counts and preservation of applied filters. Ruff passed for the three modified Python modules.

`node scripts/check_home_motion.mjs` checks the running app at localhost:8501 with local Chrome, using Node >=22 without npm dependencies. Browser checks confirmed all four point selections, image loading, paused background and scene animations, no horizontal overflow at 1440 and 390 pixels, and disabled background animation under reduced-motion preference.

- [Desktop capture](screenshots/homepage-lovable-motion-desktop.png)
- [Mobile capture](screenshots/homepage-lovable-motion-mobile.png)

Checks use Chrome viewport emulation. Physical touch devices, other browser engines and a full accessibility audit have not been tested.
