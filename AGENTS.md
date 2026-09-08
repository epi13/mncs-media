# Agent and contributor contract

- Prefer `mncs-language` for framework logic and pressure implementations.
- Do not reinvent complex codecs merely to avoid a well-defined FFI; isolate external codec boundaries behind typed MNCS interfaces.
- Treat media bytes and metadata as untrusted input.
- Timebases, timestamps, channel/pixel formats and conversion loss must be explicit.
- Streaming paths must expose bounds, backpressure and lifecycle.
- Record language/compiler/runtime/FFI pressure in `docs/LANGUAGE_PRESSURES.md`.
- Validate transforms with known fixtures and round-trip or metric-based tests where meaningful.
