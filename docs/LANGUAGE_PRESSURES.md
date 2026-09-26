# MNCS language pressure ledger

Record workload, observed behavior, required semantic, reproducer, owner, workaround and closure verification.

## Initial pressure targets

- efficient byte buffers, slices and views
- ownership/lifetime transfer across FFI
- safe ref-counted/shared frame buffers where needed
- tagged unions/enums for rich media formats
- rational/timebase and timestamp arithmetic
- async bounded streams and backpressure
- zero-copy pipeline composition
- SIMD-friendly pixel/sample layouts
- GPU buffer ownership and transfer
- dynamic plugin/format capability discovery without abandoning type safety
- structured codec/parser errors with byte/track context
- diagnostics around incompatible formats/conversions

## Campaign findings (2026-09-26, image foundation slice)

- **M-001 (non-blocking, language): fixed-size byte arrays carry
  buffers honestly but verbosely.** `[byte; 16]`/`[byte; 48]` tiles
  with integer literals adapting to `byte` elaborated with no
  friction; `as` conversions cross to u64 for magic comparison.
  Pressure remains for *large* buffers (slices/views, zero-copy,
  ref-counted frames) — untested here by design; the bounded-tile
  path deliberately does not pretend to cover it. Owner: language
  buffer/slice semantics (future streaming slice must re-test).
- **M-002 (non-blocking, language): reserved words bite natural
  names.** `over` cannot be a binding (`iterate…over`). Same class
  as control C-001 (`next`). Workaround: rename. Owner: language
  diagnostic guidance; no semantic gap.
- **M-003 (non-blocking, architecture): resampling convention must
  be declared, not assumed.** PIL NEAREST 4→2 samples pixel centers;
  the native kernel samples top-lefts. Both exact, mutually
  inconsistent unless the convention is part of the spec. Media
  records conventions in kernel docs and pins both in integration
  checks. Owner: Media spec discipline (done); backends must publish
  theirs.
- **M-004 (non-blocking, numeric): rational timebase needs no new
  primitives.** u64 num/den + bounded Euclid GCD + cross-multiplied
  equality covered NTSC and frame/duration round-trips exactly. No
  float fps anywhere. If a generic Time subsystem emerges elsewhere,
  this rational core is adoptable, not conflicting.
- **M-005 (non-blocking, test/ arch): lossy-codec verification is a
  methods gap, not a code gap.** Lossless PNG allowed exact-byte
  assertions; the first lossy backend will need tolerance/metric
  policy (no perceptual metrics invented here). Recorded so the
  audio/video slices budget for it.

Deferred (decided, not pressure): async bounded streams (whole-frame
bounded path suffices for the slice; Signal relationship unevaluated
until a streaming slice exists); SIMD/GPU layouts (no native pixel
hot loop at this scale); plugin discovery (backend codes are closed
enums + explicit `Unmapped`); hardware buffer ownership.
