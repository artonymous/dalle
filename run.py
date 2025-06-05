#!/usr/bin/env python3
"""
build_thumbs.py  –  version 3
• Makes 128-px thumbnails under .thumbs/
• Re-creates file_structure.json with {name, thumb}
Requires: pillow  (pip install pillow)
"""

from pathlib import Path
from PIL import Image
import json, sys

# ─── CONFIG ─────────────────────────────────────────────────────────────
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
THUMB_SIZE = 128
ROOT       = Path.cwd().resolve()
THUMB_ROOT = ROOT / "thumbs"
JSON_OUT   = ROOT / "file_structure.json"

print(">>> build_thumbs.py running from", ROOT)

# ─── THUMBNAIL HELPERS ─────────────────────────────────────────────────
def to_thumb_path(src: Path) -> Path:
    """Return absolute path where thumbnail should live."""
    rel = src.relative_to(ROOT).with_suffix(".png")
    return THUMB_ROOT / rel          # absolute

def make_thumb(src: Path):
    dst = to_thumb_path(src)
    dst.parent.mkdir(parents=True, exist_ok=True)

    # skip if up-to-date
    if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
        return

    try:
        img = Image.open(src).convert("RGB")
        img.thumbnail((THUMB_SIZE, THUMB_SIZE))
        img.save(dst, format="PNG")
        print("[thumb] ", dst.relative_to(ROOT))
    except Exception as e:
        print("[WARN]  cannot thumbnail", src, "→", dst, ":", e)

# ─── JSON BUILDER ───────────────────────────────────────────────────────
def build_tree(folder: Path):
    node = {"type": "folder", "name": folder.name or "root", "children": []}

    for entry in sorted(folder.iterdir()):
        if entry.name == ".thumbs":           # don’t recurse into thumb tree
            continue
        if entry.is_dir():
            node["children"].append(build_tree(entry))
        elif entry.suffix.lower() in IMAGE_EXTS:
            make_thumb(entry)
            node["children"].append({
                "type":  "file",
                "name":  entry.name,
                "thumb": str(to_thumb_path(entry).relative_to(ROOT).as_posix())
            })
    return node

# ─── MAIN ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        tree = build_tree(ROOT)
        JSON_OUT.write_text(json.dumps(tree, indent=2))
        print(">>> wrote", JSON_OUT.relative_to(ROOT))
        print("Done.")
    except Exception as err:
        print("Fatal:", err)
        sys.exit(1)