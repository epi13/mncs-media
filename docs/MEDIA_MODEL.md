# Media model and ownership boundary

## The smallest generic abstraction (as implemented)

Media = **typed descriptions of what bytes mean** plus **typed plans
for what to do with them**, executed by trusted backends:

- *Descriptions*: kind, container vs codec, pixel/sample format,
  logical dims, rational timebase, stream layout, content identity.
- *Plans*: resize/crop/convert specs with computed output geometry
  and an explicit metadata policy.
- *Proofs*: probe outcomes, budget checks, pixel-exact tile kernels,
  structured failures.

Everything else — codec math, container parsing, resampling bytes,
file I/O, scheduling — lives behind the backend contract.

## Concept classification (from the RFC evidence)

- **Foundational Media**: image descriptors, pixel formats, stream
  descriptors, probe results, resize/crop specs + output geometry,
  conversion loss classes, rational timebase, budgets, failure
  taxonomy, native tile pixel ops.
- **Backend/codec**: PNG encode/decode, resampling bytes, container
  parsing, EXIF/text-chunk handling (Pillow/FFmpeg via the adapter).
- **Data**: generic tables/digests — `mncs-data`'s `image.mncs` is
  table snapshotting, no overlap, no dependency.
- **Geometry**: generic points/vectors — crop/resize math stays
  integer-explicit in Media (u64 lanes); no geometry dependency at
  this scale, no duplication either.
- **Signal/streaming**: async frame/sample streams are future scope;
  nothing here overlaps Signal today (recorded pressure, not code).
- **Host/platform**: file I/O, process invocation, GPU paths —
  behind `tools/media_backend.py`, documented as host-owned.
- **Deferred, not obsolete**: audio/video backends, orientation
  normalization, color management, streaming framework, hardware
  acceleration. Declared in descriptors/RFC, implemented when a
  vertical slice needs them.

## Encoded vs decoded (load-bearing distinction)

- *Encoded*: compressed/container bytes (PNG file). Probe reads
  metadata without full decode where the backend allows.
- *Decoded*: frames/pixels/samples with a stated format (RGB triples,
  gray bytes). Native `pixels` kernels operate only here.
- Plans never hide cost: `probe` is cheap metadata; `decode`,
  `resize`, `encode` are explicitly effectful backend operations.

## Format identity (no `format: string`)

Container (`Png`, `Raw`) ≠ codec (`PngCodec`, `RawSamples`) ≠ pixel
format (`Gray8`, `Rgb8`, `Rgba8`) ≠ backend observation (ffprobe
`pix_fmt: rgb24` carried as evidence, not as the model). Backend
pixel codes map through `parse_pixfmt`; unmapped codes stay
`Unmapped`.

## Metadata (three piles, not one map)

- *Structural*: dims, format, streams, timebase — required to
  interpret the media, owned by descriptors.
- *Descriptive*: Title/text keys — preserved through load (pinned),
  policy per plan (`Preserved`/`Rewritten`/`Dropped`).
- *Provenance*: backend identity + version per result, fixture
  manifest, transform parameters. Lineage owns derivation graphs;
  Media preserves the hooks (source identity, op, params, output
  identity) without building a history database. Rights: Media
  extracts/preserves rights-adjacent metadata only; rights-provenance
  interprets it (active repo, untouched).

## Time

Rational `num`/`den` rates, integer-microsecond durations with
explicit truncation order, GCD reduction, cross-multiplied equality.
30000/1001 needs no float. No calendar semantics; no private time
library (a generic Time subsystem, if it emerges elsewhere, can be
adopted — the rational core here is compatible, not conflicting).

## Orientation / color (honest limits)

EXIF orientation is preserved as metadata, not normalized; width and
height always mean coded order. Color: formats name channels, not
colorimetry; RGB→gray luma is `BackendDefined`, never silently
assumed. Nothing is discarded without a policy flag.

## Resource posture

Budgets (max lane, max bytes) are checked from *declared* dims before
trust; lane check precedes byte multiplication. Decode bombs are
`LaneTooLarge`/`OverBytes` data. Backend runs under argv + timeouts
with bounded logs; malformed input is `MALFORMED`/`TRUNCATED`, never
a crash (pinned with trunc40.bin).

## Manifests: media as a projection of development state

`mncs.media.manifest.v1` binds one media artifact to the development
state it was derived from. A manifest carries the artifact kind, the
source canonical generation, the derivation chain (parent manifest
identities for derived artifacts), content binding, provenance, and
an optional publication receipt link. Admission is native:
content binding and provenance are required, derived artifacts must
name parents, and only `Admitted` manifests may be receipted or
cross-linked.

Validity and executability stay separate: audio/video manifests
admit as descriptors while backend execution remains image-only
(`backend_executable`), so dispatchers never silently no-op a kind
the backend cannot process. `derivation_current` marks a derived
artifact older than its parent stale; `publication_claim_ok`
requires a linked receipt for published claims.

Wire shape (`mncs.media-manifest/1`):

```json
{"schema_version": "mncs.media-manifest/1", "artifact": "sha256:...",
 "kind": "image", "content": "sha256:...", "semantic": {"dims": [8, 6]},
 "derivation": ["sha256:parent"], "provenance": "sha256:...",
 "source_generation": 5, "descriptor_only": false,
 "targets": [], "receipt": null}
```

Session evidence feeds manifests through `mncs.session-evidence/1`:

```json
{"schema_version": "mncs.session-evidence/1", "generation": 5,
 "commands": [], "tests": [], "diffs": [], "diagnostics": [],
 "narrative": null, "provenance": "sha256:..."}
```

Reconcilers compare manifests, publishers receipt them, and
downstream projections (journal, Atlas, website) cross-link from
receipts. Video assembly, terminal replay, diagram generation, and
external publishers (YouTube/Reddit/RSS) are greenfield consumers
of this contract: they take session evidence plus manifests and
emit receipts, and are never hard-coded as architecture. See
mncs-automation RFC 0002 for the reconciliation loop and mncs-store
RFC 0020 for receipt bytes.
