# Fixture corpus (generated, rights-clean)

Every file here is synthesized by `python3 tools/media_backend.py
gen-fixtures tests/fixtures` (Pillow 12.3.0). No third-party bytes;
no licensing exposure. Regeneration is deterministic; `MANIFEST.json`
records the generator and backend version.

- `grad8x6.png` — 8x6 RGB gradient (R=x*32, G=y*40, B=(x+y)*16).
  Vertical-slice source.
- `rgb4x4.png` — 4x4 RGB (R=x*64, G=y*64, B=128). Native NN vectors.
- `alpha4x4.png` — 4x4 RGBA, varying alpha. Convert-plan vectors.
- `gray4x4.png` — 4x4 gray ramp `(y*4+x)*16`. Native NN/crop vectors.
- `meta8x6.png` — gradient copy + `Title` tEXt chunk. Preservation vector.
- `trunc40.bin` — first 40 PNG bytes (no IDAT). Malformed vector.
- `notpng.bin` — wrong magic. Sniff-negative vector.
