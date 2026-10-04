# Shared Asset Reuse System

Use the project asset library at `asset-library/` as the first source for every episode. The library is a production cache, not a loose inspiration folder.

## Pre-generation gate

Before any ChatCut `gpt-image-2` call:

1. Turn the approved shot list into an `episode-assets.json` file.
2. Give every need a scene id, asset type, optional character id, and semantic/action tags.
3. Run:

   ```bash
   npm run assets:resolve -- --input <episode-assets.json>
   ```

4. Read the generated `.asset-resolution.md` and `.json`.
5. Act on the verdict:
   - `reuse`: use the indexed file unchanged.
   - `adapt`: derive grayscale, crop, recolor, resize, or separate layers without generating a new subject.
   - `generate`: call `gpt-image-2` only for the exact missing pose, interaction, prop state, or environment.

Do not generate a replacement merely because a reusable asset is not already inside the current episode folder.

## Admission gate

New media is not reusable merely because it exists.

- Put new files in `asset-library/incoming/`.
- Confirm style, character continuity, action accuracy, dimensions, alpha, safe crop, and absence of baked subtitles.
- Register approved files in `asset-library/library.json`.
- Run `npm run assets:validate`.
- Move failed material to `asset-library/rejected/` or keep it episode-local.

Only `status: "approved"` entries are eligible for automatic reuse.

## Character reuse

- Read `asset-library/cast.json` before inventing a new protagonist.
- Prefer an approved recurring character when that identity plausibly fits the topic.
- A recurring character may change temporary props, outerwear, and scene context, but not face, age, hair, body proportion, or signature clothing palette.
- Match both action and emotion. A neutral standing pose cannot represent running, pleading, typing, shock, or object handoff.
- Hand-object contact is a hard condition. If the library does not have the required interaction, generate that exact pose and add it after approval.

## Common assets

Use editable SVG overlays and props for arrows, evidence cards, relation lines, phones, contracts, shopping baskets, coins, calendars, and paper backgrounds. Recoloring or restacking these assets is preferred to regenerating equivalent raster artwork.

Use a generated environment only when the location itself carries story information. Keep reusable environments free of people, captions, logos, and story-specific numbers.

## Episode-local manifest

Every final episode keeps its own manifest and may copy or link reused files into its deliverable folder. The authoritative source remains `asset-library/library.json`; do not fork an untracked duplicate and later treat it as a new asset.

