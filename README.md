# mncs-media

High-level machine-native media infrastructure for MNCS.

`mncs-media` provides ergonomic image, audio, video and metadata pipelines while pressuring `mncs-language` on binary I/O, streaming, async execution, zero-copy buffers, external codec boundaries, time-based media, SIMD/GPU transforms and format-rich error handling.

## Initial scope

- media/frame/sample and metadata abstractions
- image/audio/video timing and timebase primitives
- container/format probing boundaries
- decode/encode interfaces to established codec implementations
- transforms, resizing/resampling and conversion pipelines
- bounded streaming and backpressure
- metadata preservation and explicit loss policies
- CPU/SIMD/GPU acceleration and verification

## Repository layout

- `docs/ARCHITECTURE.md`
- `docs/rfcs/0001-foundation.md`
- `docs/LANGUAGE_PRESSURES.md`
- `AGENTS.md`
