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
