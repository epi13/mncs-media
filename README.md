# mncs-media

High-level machine-native media infrastructure for MNCS.

`mncs-media` is the first and only canonical Media implementation: no
`media-v1/v2`, no parallel host/native systems, no compatibility
layers (there was no legacy implementation to be compatible with).
It owns **media semantics** — descriptors, formats, streams, time,
transform specs, budgets, failures — written substantially in
`mncs-language` (Profile 0.18), and orchestrates **established
backends** (Pillow, FFmpeg) through a narrow typed contract for the
byte-level work it must not reinvent.

## Ownership boundary

| Concern | Owner | Media relationship |
|---|---|---|
| Scalar/byte arithmetic, folds, conversions | Language core/std, `mncs-numerics` | Consumed; never duplicated |
| 8x8 pixel substrate / visual observer | `mncs.core.image` / `vision` (language) | Respected; Media works at media scale, not re-implemented |
| Generic tables/digests | `mncs-data` | Its `image.mncs` is table snapshots, unrelated; no dependency |
| Geometric primitives | `mncs-geometry` | Crop/resize geometry kept integer-explicit in Media; no duplication |
| Codecs, container parsing, resampling bytes | Pillow 12.3.0 / FFmpeg 8.1.2 (host) | Used via `tools/media_backend.py`; never re-implemented |
| Persistence, execution, planning, rights | Store / Forge+Fabric / RAVEL / rights-provenance | Not owned; lineage/provenance hooks preserved |
| Pixel formats, dims, timebase, streams, specs, budgets, failures | **`mncs-media`** | Canonical home |

## Current capability (image foundation slice)

- `src/media/pixfmt.mncs` — Gray8/Rgb8/Rgba8 descriptors, backend-code
  mapping (unmapped, never guessed), conversion loss classes.
- `src/media/dims.mncs` — logical dims, crop discipline (OOB/empty
  rejected), exact integer fit/fill/stretch geometry.
- `src/media/timebase.mncs` — rational rates, GCD reduction, exact
  equality, frame/duration conversion (serves future audio/video too).
- `src/media/sniff.mncs` — 8-byte magic sniffing (total, no guessing).
- `src/media/descriptor.mncs` — content vs location vs semantic
  identity, stream descriptors, probe outcomes, frame byte counts.
- `src/media/transform.mncs` — resize/crop/convert plans with explicit
  metadata policy (Preserved/Rewritten/Dropped).
- `src/media/pixels.mncs` — native top-left NN downscale (gray8, rgb)
  and gray crop on bounded tiles, byte-exact.
- `src/media/limits.mncs` — lane/byte budgets checked before trust.
- `src/media/failures.mncs` — 10-code taxonomy with bounded context.

## Vertical slice (operational)

Generated 8x6 RGB PNG → PIL+ffprobe probe → MNCS descriptor/plans →
backend crop/resize → MNCS pixel-exact verification + metadata
preservation check. Audio/video backends are declared descriptor
scope, not implemented operations.

## Verification

29 native `mncs test` declarations, 7/7 suites PASS
(`scripts/run_tests.py`); 17/17 backend integration checks
(`scripts/run_backend_checks.py`, incl. PIL↔ffprobe agreement and the
documented resampling-convention difference). Fixtures are generated,
rights-clean (`tests/fixtures`, see its README).

## Backend boundary

`tools/media_backend.py` (argv in, JSON out, bounded logs) is the only
codec-touching code. Version provenance (Pillow/FFmpeg) is recorded
per result. See `docs/MEDIA_MODEL.md` and `docs/VERIFICATION.md`.

## Layout

- `src/media/` — MNCS semantics (`.mncs` only)
- `tests/native/` — in-language contracts; `tests/fixtures/` — generated corpus
- `scripts/run_tests.py` — native runner; `scripts/run_backend_checks.py` — boundary checks
- `tools/media_backend.py` — Pillow/FFmpeg adapter
- `docs/` — model, verification, pressures, RFC record
- `evidence/media-capabilities.json` — machine-readable capability record
