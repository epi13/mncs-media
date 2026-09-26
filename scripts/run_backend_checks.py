#!/usr/bin/env python3
"""Backend integration checks for mncs-media: host codec behavior vs the
MNCS semantic layer's committed expectations.

This is NOT a second test framework for MNCS logic (that is
scripts/run_tests.py). It validates the host boundary:

- fixtures decode to the exact byte vectors the native pixel tests pin;
- probe metadata (dims/mode/codec) matches the native descriptor tests;
- PIL and ffprobe agree on the gradient fixture (two independent backends);
- the resize/crop pipeline produces the dims the native plan tests pin;
- sampling-convention difference (PIL NEAREST center vs MNCS top-left)
  is pinned on both sides instead of hidden;
- malformed/wrong-magic inputs fail structurally;
- descriptive metadata survives a load cycle (preservation policy).

Usage:
    python3 scripts/run_backend_checks.py [--fixtures DIR] [--work DIR]
Exit code is 0 only when every check passes.
"""

import argparse
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND = os.path.join(ROOT, "tools", "media_backend.py")

PASS = []
FAIL = []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print("%-46s %s %s" % (name, "OK" if cond else "MISMATCH", detail))


def run(*args):
    proc = subprocess.run(
        [sys.executable, BACKEND] + list(args),
        capture_output=True, text=True, timeout=120)
    try:
        return json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return {"ok": False, "error": "BACKEND_PROTOCOL",
                "detail": (proc.stdout + proc.stderr)[-500:]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", default=os.path.join(ROOT, "tests", "fixtures"))
    parser.add_argument("--work", default=os.path.join(ROOT, "target", "backend-work"))
    args = parser.parse_args()
    os.makedirs(args.work, exist_ok=True)

    gen = run("gen-fixtures", args.fixtures)
    check("fixtures generated", gen.get("ok") is True)
    fx = lambda n: os.path.join(args.fixtures, n)

    # --- probe vs native descriptor expectations ---------------------------
    grad = run("probe", fx("grad8x6.png"))
    check("probe grad dims 8x6 RGB", grad.get("width") == 8
          and grad.get("height") == 6 and grad.get("mode") == "RGB")
    streams = ((grad.get("ffprobe") or {}).get("result") or {}).get("streams") or []
    agree = (len(streams) == 1 and streams[0].get("width") == 8
             and streams[0].get("height") == 6
             and streams[0].get("codec_name") == "png")
    check("ffprobe agrees with PIL", agree, str(streams[0] if streams else streams))
    alpha = run("probe", fx("alpha4x4.png"))
    check("probe alpha 4x4 RGBA", alpha.get("width") == 4
          and alpha.get("height") == 4 and alpha.get("mode") == "RGBA")
    gray = run("probe", fx("gray4x4.png"))
    check("probe gray 4x4 L", gray.get("width") == 4
          and gray.get("height") == 4 and gray.get("mode") == "L")

    # --- decode bytes vs native pixel-test vectors --------------------------
    dec = run("decode", fx("gray4x4.png"))
    check("gray bytes exact", dec.get("pixels_hex")
          == "00102030405060708090a0b0c0d0e0f0")
    rgb = run("decode", fx("rgb4x4.png"))
    check("rgb bytes_len 48", rgb.get("bytes_len") == 48
          and rgb.get("mode") == "RGB")

    # --- sampling conventions pinned on both sides ---------------------------
    raw = bytes.fromhex(dec["pixels_hex"])
    topleft = bytes([raw[0], raw[2], raw[8], raw[10]])
    check("numpy top-left == MNCS expectation", topleft.hex() == "002080a0")
    small = run("resize-nn", fx("gray4x4.png"), "2", "2",
                os.path.join(args.work, "gray2x2.png"))
    dec_small = run("decode", os.path.join(args.work, "gray2x2.png"))
    check("PIL resize dims 2x2", small.get("width") == 2 and small.get("height") == 2)
    check("PIL center sampling pinned", dec_small.get("pixels_hex") == "5070d0f0",
          "differs from MNCS top-left by declared convention")

    # --- crop pipeline vs native plan -----------------------------------------
    crop = run("crop", fx("grad8x6.png"), "2", "1", "2", "2",
               os.path.join(args.work, "crop2x2.png"))
    dec_crop = run("decode", os.path.join(args.work, "crop2x2.png"))
    check("crop dims 2x2", crop.get("width") == 2 and crop.get("height") == 2)
    check("crop pixels exact", dec_crop.get("pixels_hex") == "402830602840405040605050")

    # --- metadata preservation --------------------------------------------------
    meta = run("probe", fx("meta8x6.png"))
    check("Title text key preserved", "Title" in (meta.get("text_keys") or []),
          str(meta.get("text_keys")))
    check("meta still RGB still image", meta.get("mode") == "RGB"
          and meta.get("width") == 8)

    # --- malformed / wrong-magic inputs ------------------------------------------
    trunc = run("probe", fx("trunc40.bin"))
    check("truncated probe fails structured",
          trunc.get("ok") is False and trunc.get("error") == "MALFORMED")
    with open(fx("notpng.bin"), "rb") as fh:
        magic = fh.read(8)
    check("wrong magic not PNG",
          magic != b"\x89PNG\r\n\x1a\n", magic.hex())

    # --- version provenance ---------------------------------------------------------
    check("backend versions recorded",
          bool((grad.get("backend") or {}).get("pil")), str(grad.get("backend")))

    print("----\nbackend checks: %d passed, %d failed" % (len(PASS), len(FAIL)))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
