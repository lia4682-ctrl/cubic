#!/usr/bin/env python3
"""
images/ 폴더를 훑어서 gallery-data.js 를 갱신합니다.

사용법:  python make_manifest.py

- 새로 넣은 이미지는 자동으로 목록에 추가됩니다.
- 이미 적어둔 제목/태그는 그대로 유지됩니다.
- 폴더에서 지운 이미지는 목록에서도 빠집니다.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).parent
IMG_DIR = ROOT / "images"
DATA_FILE = ROOT / "gallery-data.js"
EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".avif"}

DEFAULT_SITE = {
    "title": "큐빅 이미지 무료 다운로드",
    "subtitle": "마음에 드는 이미지를 골라 바로 받아가세요.",
    "license": "자유롭게 사용하실 수 있어요. 재배포 시 출처를 남겨주세요.",
}


def load_existing():
    if not DATA_FILE.exists():
        return {"site": DEFAULT_SITE, "images": []}
    text = DATA_FILE.read_text(encoding="utf-8")
    m = re.search(r"window\.GALLERY\s*=\s*(\{.*\})\s*;?\s*$", text, re.S)
    if not m:
        print("! gallery-data.js 형식을 읽지 못해 새로 만듭니다.")
        return {"site": DEFAULT_SITE, "images": []}
    return json.loads(m.group(1))


def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def title_from(name):
    stem = Path(name).stem
    return re.sub(r"[-_]+", " ", stem).strip() or name


def main():
    IMG_DIR.mkdir(exist_ok=True)
    data = load_existing()
    site = {**DEFAULT_SITE, **data.get("site", {})}
    old = {i["file"]: i for i in data.get("images", [])}

    on_disk = sorted(
        (p.name for p in IMG_DIR.iterdir() if p.suffix.lower() in EXTS),
        key=natural_key,
    )
    disk_set = set(on_disk)

    images = [old[f] for f in old if f in disk_set]  # 기존 순서 유지
    added = [f for f in on_disk if f not in old]
    for f in added:
        images.append({"file": f, "title": title_from(f), "tags": []})

    removed = [f for f in old if f not in disk_set]

    out = {"site": site, "images": images}
    DATA_FILE.write_text(
        "window.GALLERY = " + json.dumps(out, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(f"완료: 총 {len(images)}개 (추가 {len(added)}, 제거 {len(removed)})")
    if added:
        print("  새로 추가됨:", ", ".join(added))
    if removed:
        print("  목록에서 빠짐:", ", ".join(removed))
    print("제목/태그는 gallery-data.js 에서 직접 고칠 수 있어요.")


if __name__ == "__main__":
    main()
