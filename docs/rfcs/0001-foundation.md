# RFC 0001: Media pipeline foundation

Status: Draft

## Principles

- Binary media input is untrusted and parsers/codec adapters return structured errors.
- Timestamp and timebase semantics are explicit rather than inferred from raw numbers.
- Streaming pipelines are bounded or explicitly documented otherwise and support backpressure/cancellation.
- External codecs are isolated behind typed interfaces; FFI does not leak arbitrary ownership into application code.
- Metadata preservation, normalization and intentional loss are distinct operations.
- Acceleration may change physical execution but not declared transform meaning/tolerance.

## Pressure objectives

Byte buffers/slices, ownership across FFI, tagged unions for formats, async streams, zero-copy/ref-counted frame lifetimes, time/duration rational types, plugin/format discovery, structured errors, SIMD/GPU transforms, pinned/shared memory and ergonomic conversion APIs.
