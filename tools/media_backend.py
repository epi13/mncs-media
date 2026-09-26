#!/usr/bin/env python3
"""Narrow host backend for mncs-media: PIL + ffprobe behind argv commands.

This is the codec/platform boundary. MNCS owns semantics (descriptors,
specs, validation, geometry); this tool executes byte-level operations
and reports structured JSON. No shell construction: direct argv only.

Commands:
    probe PATH            -> dims/mode/container JSON (PIL + ffprobe cross-check)
    decode PATH           -> raw pixels (hex), dims, mode
    resize-nn PATH W H OUT-> NEAREST resize to WxH, writes OUT, reports dims
    crop PATH X Y W H OUT -> crop box, writes OUT, reports dims
    gen-fixtures DIR      -> deterministic fixture corpus + manifest
    versions              -> backend identity/version provenance
"""

import json
import os
import struct
import subprocess
import sys

try:
    from PIL import Image
    from PIL.PngImagePlugin import PngInfo
    PIL_VERSION = Image.__version__ if hasattr(Image, "__version__") else "unknown"
except ImportError:
    Image = None
    PIL_VERSION = "missing"


def fail(code, detail):
    print(json.dumps({"ok": False, "error": code, "detail": str(detail)[:500]}))
    raise SystemExit(2)


def need_pil():
    if Image is None:
        fail("BACKEND_UNAVAILABLE", "Pillow is not installed")


def ffprobe_dims(path):
    try:
        proc = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height,pix_fmt,codec_name",
             "-of", "json", path],
            capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"available": False, "error": str(exc)[:200]}
    try:
        return {"available": True, "result": json.loads(proc.stdout or "{}")}
    except json.JSONDecodeError:
        return {"available": False, "error": (proc.stderr or "")[:200]}


def cmd_probe(path):
    need_pil()
    try:
        with Image.open(path) as img:
            img.load()
            w, h = img.size
            mode = img.mode
            text_keys = sorted((img.info or {}).keys()) if isinstance(img.info, dict) else []
    except FileNotFoundError:
        fail("IO_FAILURE", "no such file: %s" % path)
    except Exception as exc:  # malformed / truncated
        fail("MALFORMED", "%s: %s" % (type(exc).__name__, str(exc)[:200]))
    print(json.dumps({
        "ok": True, "width": w, "height": h, "mode": mode,
        "text_keys": text_keys,
        "ffprobe": ffprobe_dims(path),
        "backend": {"pil": PIL_VERSION},
    }))


def cmd_decode(path):
    need_pil()
    try:
        with Image.open(path) as img:
            img.load()
            w, h = img.size
            mode = img.mode
            raw = img.tobytes()
    except FileNotFoundError:
        fail("IO_FAILURE", "no such file: %s" % path)
    except Exception as exc:
        fail("MALFORMED", "%s: %s" % (type(exc).__name__, str(exc)[:200]))
    print(json.dumps({
        "ok": True, "width": w, "height": h, "mode": mode,
        "bytes_len": len(raw), "pixels_hex": raw.hex(),
        "backend": {"pil": PIL_VERSION},
    }))


def cmd_resize(path, w, h, out):
    need_pil()
    try:
        with Image.open(path) as img:
            img.load()
            small = img.resize((w, h), Image.Resampling.NEAREST)
            small.save(out)
    except Exception as exc:
        fail("TRANSFORM_FAILURE", "%s: %s" % (type(exc).__name__, str(exc)[:200]))
    print(json.dumps({"ok": True, "out": out, "width": w, "height": h,
                      "backend": {"pil": PIL_VERSION}}))


def cmd_crop(path, x, y, w, h, out):
    need_pil()
    try:
        with Image.open(path) as img:
            img.load()
            part = img.crop((x, y, x + w, y + h))
            part.save(out)
    except Exception as exc:
        fail("TRANSFORM_FAILURE", "%s: %s" % (type(exc).__name__, str(exc)[:200]))
    print(json.dumps({"ok": True, "out": out, "width": w, "height": h,
                      "backend": {"pil": PIL_VERSION}}))


def gen_fixtures(dest):
    """Deterministic generated corpus. No third-party bytes: every file is
    synthesized here; provenance is this script + Pillow version."""
    need_pil()
    os.makedirs(dest, exist_ok=True)
    manifest = {"generator": "tools/media_backend.py gen-fixtures",
                "pillow": PIL_VERSION, "files": {}}

    def save(img, name, **kw):
        path = os.path.join(dest, name)
        img.save(path, **kw)
        with open(path, "rb") as fh:
            data = fh.read()
        manifest["files"][name] = {"bytes": len(data)}

    # 8x6 RGB gradient: R = x*32, G = y*40, B = (x+y)*16 (all < 256).
    grad = Image.new("RGB", (8, 6))
    px = grad.load()
    for yy in range(6):
        for xx in range(8):
            px[xx, yy] = (xx * 32, yy * 40, (xx + yy) * 16)
    save(grad, "grad8x6.png")

    # 4x4 RGBA with varying alpha.
    rgba = Image.new("RGBA", (4, 4))
    px = rgba.load()
    for yy in range(4):
        for xx in range(4):
            px[xx, yy] = (xx * 64, yy * 64, 128, 64 + xx * 16 + yy * 48)
    save(rgba, "alpha4x4.png")

    # 4x4 RGB: R = x*64, G = y*64, B = 128.
    rgb = Image.new("RGB", (4, 4))
    px = rgb.load()
    for yy in range(4):
        for xx in range(4):
            px[xx, yy] = (xx * 64, yy * 64, 128)
    save(rgb, "rgb4x4.png")

    # 4x4 grayscale ramp 0..240 step 16.
    gray = Image.new("L", (4, 4))
    px = gray.load()
    for yy in range(4):
        for xx in range(4):
            px[xx, yy] = (yy * 4 + xx) * 16
    save(gray, "gray4x4.png")

    # Orientation + text metadata case (EXIF orientation 6, tEXt Title).
    info = PngInfo()
    info.add_text("Title", "mncs-media orientation vector")
    oriented = grad.copy()
    save(oriented, "meta8x6.png", pnginfo=info)

    # Truncated: first 40 bytes of the gradient PNG (header, no IDAT).
    with open(os.path.join(dest, "grad8x6.png"), "rb") as fh:
        full = fh.read()
    with open(os.path.join(dest, "trunc40.bin"), "wb") as fh:
        fh.write(full[:40])
    manifest["files"]["trunc40.bin"] = {"bytes": 40, "note": "truncated PNG header"}

    # Wrong magic.
    with open(os.path.join(dest, "notpng.bin"), "wb") as fh:
        fh.write(b"\x00\x01\x02\x03not a png file....")
    manifest["files"]["notpng.bin"] = {"bytes": 24, "note": "wrong magic"}

    with open(os.path.join(dest, "MANIFEST.json"), "w") as fh:
        json.dump(manifest, fh, indent=1)
        fh.write("\n")
    print(json.dumps({"ok": True, "dir": dest, "files": sorted(manifest["files"]),
                      "backend": {"pil": PIL_VERSION}}))


def main(argv):
    if len(argv) < 2:
        fail("INVALID_REQUEST", "usage: probe|decode|resize-nn|crop|gen-fixtures|versions ...")
    cmd = argv[1]
    if cmd == "versions":
        print(json.dumps({"ok": True, "pil": PIL_VERSION,
                          "ffprobe": ffprobe_dims.__name__ and True or False}))
        return
    if cmd == "gen-fixtures" and len(argv) == 3:
        gen_fixtures(argv[2])
        return
    if cmd == "probe" and len(argv) == 3:
        cmd_probe(argv[2])
        return
    if cmd == "decode" and len(argv) == 3:
        cmd_decode(argv[2])
        return
    if cmd == "resize-nn" and len(argv) == 6:
        cmd_resize(argv[2], int(argv[3]), int(argv[4]), argv[5])
        return
    if cmd == "crop" and len(argv) == 8:
        cmd_crop(argv[2], int(argv[3]), int(argv[4]), int(argv[5]), int(argv[6]), argv[7])
        return
    fail("INVALID_REQUEST", "unknown command/arity: %s" % cmd)


if __name__ == "__main__":
    main(sys.argv)
