# Scientific verification

## Native layer (29 declarations, 7/7 suites PASS)

- **pixfmt**: channel counts, alpha flags, backend-code mapping with
  explicit `Unmapped`, all four conversion classes.
- **dims**: zero-lane rejection; in-frame/full-frame crops; OOB,
  past-origin, and empty crops rejected; stretch/fit/fill geometry
  exact (8x6→4x4 fit = 4x3; tall 6x8→4x4 fit = 3x4; fill window
  centered 6x6 at x=1); bad targets rejected.
- **timebase**: NTSC 30000/1001 valid; zero den/num rejected; GCD and
  reduction (24/36→2/3); cross-multiplied equality (24/1 == 48/2);
  48 frames @24fps = exactly 2_000_000 us and back; 30000 NTSC
  frames = 1_001_000_000 us.
- **sniffdesc**: full 8-byte PNG magic recognized; wrong head and
  right-head/wrong-tail rejected; probe builds typed descriptor
  (8x6 RGB, stream 0/backend 0); frame bytes 144/64/16; content
  identity separates digest+len from location.
- **transform**: resize/crop plans compute output descriptors;
  bad source/target routed; RGBA→RGB is DropsAlpha/Dropped,
  identity is Lossless/Preserved.
- **pixels**: gray 4x4→2x2 top-left NN = `[0,32,128,160]`; rgb
  4x4→2x2 = 12 exact bytes; gray crop at (1,1) = `[80,96,144,160]`
  plus origin corner. Vectors are backend-observed fixture bytes
  (see below), not self-generated.
- **limits**: fixture scale accepted with byte count; 100000² lanes
  → `LaneTooLarge` before trust; 64x64 RGBA over 1 KiB budget →
  `OverBytes`; zero dims → `BadDims`; 10 failure codes distinct;
  backend vs modeling failures classified.

## Backend boundary (17/17 checks PASS)

PIL 12.3.0 + FFmpeg 8.1.2 (ffmpeg CLI 8.1.2) via
`tools/media_backend.py`:

- Probe dims/mode match native descriptor expectations on all
  fixtures; **PIL and ffprobe agree** on grad8x6 (png, 8x6, rgb24).
- Decoded gray bytes exactly equal the native test vectors.
- Crop (2,1,2,2) dims and pixels exact (`402830...`).
- **Resampling convention pinned on both sides**: PIL NEAREST 4→2
  samples centers (`50 70 d0 f0`); MNCS native samples top-lefts.
  Declared mismatch, each side exact — not a bug, not hidden.
- Truncated header → structured `MALFORMED`; wrong magic ≠ PNG.
- `Title` text key survives load (preservation policy evidenced);
  version provenance recorded per result.

## What is NOT claimed

No audio/video backend operations (descriptors only); no
orientation normalization; no color management; no streaming
framework (bounded whole-frame path only); no GPU paths; no
perceptual metrics (lossless PNG only, exact bytes); no fuzzing
beyond truncation/magic cases. Recorded as UNKNOWNs in evidence.
