# Architecture

## Layers

1. **Media model** — frames, samples, planes/channels, pixel/sample formats, timestamps and timebases.
2. **Containers/metadata** — probing, streams, metadata and track descriptions.
3. **Codec boundary** — typed decoder/encoder interfaces and isolated FFI adapters to established codecs.
4. **Transforms** — color/pixel conversion, resize, resample, remix and composable processing.
5. **Streaming** — async/bounded pipelines, buffering, backpressure, cancellation and synchronization.
6. **Acceleration** — SIMD/GPU transform paths and memory-transfer strategies.
7. **Verification/tooling** — fixture corpus, metadata/round-trip checks, timing evidence and pipeline inspection.

## First milestones

1. Image/frame and audio-sample types.
2. Typed byte/stream and metadata foundation.
3. One image decode/encode adapter plus simple transforms.
4. Audio streaming/timebase pressure cases.
5. Video/frame pipeline and SIMD/GPU pressure workloads.
