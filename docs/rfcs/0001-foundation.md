# RFC 0001: Media pipeline foundation

Status: Partially implemented (2026-09-26, image foundation slice)

## Disposition

- Implemented: untrusted-input structured errors (`failures`,
  `limits`, trunc40/magic vectors); explicit rational timebase;
  typed codec isolation (`tools/media_backend.py` argv/JSON
  boundary); preservation/normalization/loss as distinct plan
  policies; transform meaning pinned incl. the resampling-convention
  difference (native top-left vs PIL center).
- Superseded: nothing — no prior implementation existed.
- Deferred by decision: bounded async streams (whole-frame bounded
  path suffices); SIMD/GPU (no hot loop at this scale); plugin
  discovery (closed enums + `Unmapped`); audio/video backends;
  orientation normalization; color management.
- Unchanged: all six principles remain normative.

## Principles

- Binary media input is untrusted and parsers/codec adapters return structured errors.
- Timestamp and timebase semantics are explicit rather than inferred from raw numbers.
- Streaming pipelines are bounded or explicitly documented otherwise and support backpressure/cancellation.
- External codecs are isolated behind typed interfaces; FFI does not leak arbitrary ownership into application code.
- Metadata preservation, normalization and intentional loss are distinct operations.
- Acceleration may change physical execution but not declared transform meaning/tolerance.

## Pressure objectives

Byte buffers/slices, ownership across FFI, tagged unions for formats, async streams, zero-copy/ref-counted frame lifetimes, time/duration rational types, plugin/format discovery, structured errors, SIMD/GPU transforms, pinned/shared memory and ergonomic conversion APIs.
