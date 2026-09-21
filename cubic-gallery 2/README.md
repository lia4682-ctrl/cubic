# 큐빅 이미지 무료 다운로드 사이트

이미지를 보고, 하나씩 또는 여러 장을 ZIP으로 받을 수 있는 정적 웹사이트입니다.
서버·DB 없이 파일만 올리면 돌아가서 무료 호스팅에 그대로 배포할 수 있어요.

## 폴더 구조

```
cubic-gallery/
├─ index.html          ← 사이트 본체 (수정할 일 거의 없음)
├─ gallery-data.js     ← 이미지 목록 + 사이트 제목/설명/라이선스 문구
├─ make_manifest.py    ← images 폴더를 읽어 gallery-data.js 를 자동 갱신
└─ images/             ← 여기에 이미지를 넣으세요 (sample-cube-*.png 는 삭제)
```

## 1. 내 이미지 넣기

1. `images/` 폴더의 `sample-cube-*.png` 6장을 지웁니다.
2. 내가 만든 큐빅 이미지를 `images/` 에 넣습니다. (png, jpg, webp, gif, svg, avif)
3. 터미널에서 실행합니다.

   ```
   python make_manifest.py
   ```

   새 이미지가 자동으로 목록에 추가됩니다. 이미 적어둔 제목·태그는 유지돼요.
4. `gallery-data.js` 를 텍스트 편집기로 열어 다음을 고칩니다.
   - `site.title` / `subtitle` / `license` : 사이트 제목, 설명, 하단 라이선스 문구
   - 각 이미지의 `title`(표시 이름)과 `tags`(필터·검색용 태그)

> Python이 없다면 `gallery-data.js` 의 `images` 목록에 `{ "file": "파일명.png", "title": "이름", "tags": ["태그"] }` 를 직접 추가해도 됩니다.

## 2. 내 컴퓨터에서 확인

- `index.html` 을 더블클릭하면 바로 열립니다. (이미지 보기·개별 다운로드 OK)
- **ZIP 다운로드는 웹 서버가 필요**해서, 확인하려면 폴더에서 아래를 실행하고 `http://localhost:8000` 으로 접속하세요.

  ```
  python -m http.server 8000
  ```

## 3. 무료로 배포하기

세 가지 중 편한 쪽을 고르세요. 모두 이 폴더 그대로 올리면 됩니다.

**Netlify Drop (가장 쉬움, 계정만 있으면 끝)**
1. https://app.netlify.com/drop 접속 후 로그인
2. `cubic-gallery` 폴더를 화면에 끌어다 놓기
3. 바로 `https://무작위이름.netlify.app` 주소가 생깁니다. 사이트 설정에서 이름을 바꿀 수 있어요.

**Cloudflare Pages**
1. Cloudflare 대시보드 → Workers & Pages → Pages → Direct Upload
2. 폴더를 업로드하면 `프로젝트명.pages.dev` 주소가 생깁니다.

**GitHub Pages (업데이트를 git으로 관리하고 싶을 때)**
1. GitHub에 새 저장소를 만들고 폴더 내용을 올립니다.
2. 저장소 Settings → Pages → Branch를 `main` / root 로 지정합니다.
3. 잠시 후 `https://내아이디.github.io/저장소명/` 에서 열립니다.

> 무료 플랜의 용량·트래픽 한도는 서비스마다 다르고 바뀔 수 있으니, 이미지가 많다면 배포 전에 각 서비스의 현재 한도를 확인하세요.

## 4. 이미지 추가·수정할 때

`images/` 에 파일을 넣고 → `python make_manifest.py` → 다시 업로드(또는 git push). 끝이에요.

## 운영 팁

- **용량**: 원본이 너무 크면 로딩이 느려집니다. 미리보기용으로 충분한 크기(예: 긴 변 1000~2000px)의 PNG/WebP를 권장해요.
- **투명 배경**: 투명 PNG는 체크무늬 위에 보여서 투명 여부를 바로 알 수 있어요.
- **라이선스**: 무료 배포라도 "상업적 이용 가능 여부, 출처 표기 필요 여부"를 `license` 문구에 분명히 적어두면 분쟁을 줄일 수 있어요.
- **파일명**: 한글·공백이 있어도 동작하지만, 영문·숫자·하이픈(`cube-blue-01.png`)이 배포 시 가장 안전합니다.
- **ZIP 기능**은 브라우저에서 JSZip 라이브러리(cdnjs)를 불러와 동작합니다. 인터넷이 끊기면 ZIP만 안 되고 개별 다운로드는 그대로 됩니다.
