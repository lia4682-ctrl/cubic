#!/usr/bin/env python3
"""
새 이미지를 추가할 때 쓰는 업스케일 도구 (이 사이트의 이미지에 적용한 것과 같은 방식).

  pip install pillow numpy opencv-python-headless
  python tools/upscale_images.py 새이미지폴더 -o images

방식: 약한 노이즈 제거 → 알파 미리곱(premultiplied) 후 bicubic + 반복 역투영(IBP) 확대
      → 알파 가장자리 매끈화·흰 테두리 제거 → 여백 정리.
※ AI 초해상도가 아니라 고전적 방식이라, 원본이 아주 작으면(≈40px 이하) 선명도에 한계가 있어요.
"""
import cv2, numpy as np
from PIL import Image

TARGET_LONG = 800   # 목표 긴 변(px)
MAX_SCALE = 12      # 너무 작은 원본은 배율 상한

def pick_scale(w, h):
    long_edge = max(w, h)
    return int(min(MAX_SCALE, max(2, -(-TARGET_LONG // long_edge))))

def ibp(src, scale, iters=10, step=0.9):
    h, w = src.shape[:2]
    up = cv2.resize(src, (w*scale, h*scale), interpolation=cv2.INTER_CUBIC)
    for _ in range(iters):
        down = cv2.resize(up, (w, h), interpolation=cv2.INTER_AREA)
        err = src - down
        up = up + step * cv2.resize(err, (w*scale, h*scale), interpolation=cv2.INTER_CUBIC)
    return up

def smoothstep(x):
    x = np.clip(x, 0, 1)
    return x*x*(3-2*x)

def upscale_rgba(im, scale=None, denoise=True):
    im = im.convert("RGBA")
    arr = np.asarray(im).astype(np.float32) / 255.0
    h, w = arr.shape[:2]
    scale = scale or pick_scale(w, h)
    a = arr[..., 3]
    rgb = arr[..., :3]
    pm = rgb * a[..., None]                       # premultiply -> 투명 픽셀 색이 번지지 않게

    if denoise:
        # JPEG 블록/노이즈 완화 (색상만, 약하게)
        u8 = np.clip(pm*255, 0, 255).astype(np.uint8)
        u8 = cv2.fastNlMeansDenoisingColored(u8, None, 3, 3, 5, 15)
        pm = u8.astype(np.float32)/255.0

    pm_up = np.clip(ibp(pm, scale, iters=8), 0, 1)
    a_up = np.clip(ibp(a, scale, iters=8), 0, 1)

    # 색 복원 (unpremultiply)
    rgb_up = pm_up / np.maximum(a_up[..., None], 1e-3)
    rgb_up = np.clip(rgb_up, 0, 1)

    # 알파 가장자리: 계단(원본 픽셀 격자)이 남지 않게 먼저 부드럽게 만든 뒤, 바깥 근처에서만 조인다
    a_smooth = cv2.GaussianBlur(a_up, (0, 0), 0.5*scale)
    r = max(3, int(1.6*scale))
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*r+1, 2*r+1))
    near_out = (cv2.erode(a_up, k) < 0.08).astype(np.float32)
    near_out = cv2.GaussianBlur(near_out, (0, 0), r/3)
    a_sharp = smoothstep((a_smooth - 0.56) * 2.4 + 0.5)   # 0.56: 흰 테두리(fringe)를 살짝 깎아냄
    a_fin = near_out * a_sharp + (1-near_out) * a_up
    a_fin[a_fin < 0.01] = 0

    # 가장자리 색 오염 제거: 안쪽 색을 바깥쪽으로 확장해 테두리 색으로 사용
    core = (cv2.erode(a_fin, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*int(1.2*scale)+1,)*2)) > 0.95).astype(np.float32)
    sig = 1.5*scale
    num = cv2.GaussianBlur(rgb_up*core[..., None], (0, 0), sig)
    den = cv2.GaussianBlur(core, (0, 0), sig)[..., None]
    rgb_in = num / np.maximum(den, 1e-4)
    band = cv2.GaussianBlur((1-core), (0, 0), 0.6*scale)[..., None] * (den > 1e-3)
    rgb_up = np.clip(rgb_up*(1-0.65*band) + rgb_in*(0.65*band), 0, 1)

    # 살짝 언샤프 (색상만)
    blur = cv2.GaussianBlur(rgb_up, (0, 0), scale*0.6)
    rgb_fin = np.clip(rgb_up + 0.45*(rgb_up - blur), 0, 1)

    out = np.dstack([rgb_fin, a_fin])
    return Image.fromarray((out*255+0.5).astype(np.uint8), "RGBA"), scale

def process(im):
    """패딩 → 업스케일 → 여백 정리. 원본이 캔버스 끝에 닿아 있어도 가장자리가 잘리지 않게 한다."""
    im = im.convert("RGBA")
    PAD = 4
    arr = np.asarray(im)
    arr = np.pad(arr, ((PAD, PAD), (PAD, PAD), (0, 0)), mode="edge").copy()
    arr[:PAD, :, 3] = 0; arr[-PAD:, :, 3] = 0; arr[:, :PAD, 3] = 0; arr[:, -PAD:, 3] = 0
    up, scale = upscale_rgba(Image.fromarray(arr, "RGBA"), scale=pick_scale(*im.size))
    a = np.asarray(up)[..., 3]
    ys, xs = np.where(a > 8)
    x0, x1, y0, y1 = xs.min(), xs.max()+1, ys.min(), ys.max()+1
    m = int(round(0.03 * max(x1-x0, y1-y0)))
    box = (max(0, x0-m), max(0, y0-m), min(up.width, x1+m), min(up.height, y1+m))
    return up.crop(box), scale

def main():
    global TARGET_LONG
    import argparse
    from pathlib import Path
    ap = argparse.ArgumentParser(description="투명 PNG 이미지를 알파 인식 방식으로 업스케일합니다.")
    ap.add_argument("input", help="이미지 파일 또는 폴더")
    ap.add_argument("-o", "--out", default="upscaled", help="저장 폴더 (기본: upscaled)")
    ap.add_argument("--target", type=int, default=TARGET_LONG, help="목표 긴 변(px), 기본 800")
    args = ap.parse_args()
    TARGET_LONG = args.target
    inp = Path(args.input)
    files = sorted(inp.glob("*.png")) if inp.is_dir() else [inp]
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    for f in files:
        im = Image.open(f)
        res, s = process(im)
        res.save(out / f.name, optimize=True)
        print(f"{f.name}: {im.size} -> {res.size} (x{s})")


if __name__ == "__main__":
    main()
