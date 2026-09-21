# 큐빅 이미지 무료 다운로드 사이트

이미지를 보고, 하나씩 또는 여러 장을 ZIP으로 받을 수 있는 정적 웹사이트입니다.
서버·DB 없이 파일만 올리면 돌아가서 무료 호스팅에 그대로 배포할 수 있어요.

## 폴더 구조

```
cubic-gallery/
├─ index.html            ← 사이트 본체 (방문자용 갤러리)
├─ admin.html            ← 웹에서 이미지 업로드 (관리자용, GitHub 연동)
├─ gallery-data.js       ← 이미지 목록 + 사이트 문구 (제목·종류·색상·태그)
├─ make_manifest.py      ← images/ 를 읽어 gallery-data.js 갱신 + thumbs/ 자동 생성
├─ images/               ← 업스케일된 원본 이미지 (다운로드되는 파일, 28장)
├─ thumbs/               ← 목록용 작은 WebP (자동 생성, 로딩 속도용)
├─ tools/upscale_images.py ← 새 이미지를 같은 방식으로 업스케일하는 도구
└─ rename-map.csv        ← 원본 파일명 → 새 파일명·제목·태그 대응표 (배포 전 지워도 됨)
```

## 1. 이미지 분류 체계

각 이미지는 아래 세 가지로 정리돼 있어요. 사이트에서 **종류**와 **색상**은 필터 버튼, **태그**는 검색과 상세 화면에 쓰입니다.

| 항목 | 값 |
|---|---|
| 종류 | 큐빅 · 진주 · 레진 · 글리터 · 참 |
| 색상 | 오로라 · 화이트 · 핑크 · 퍼플 · 투명 · 멀티 · 블루 · 민트 · 옐로우 · 아이보리 · 로즈골드 |
| 태그 | 모양(하트·별·원형·물방울·리본·꽃…), 재질/분위기(파스텔·오로라·홀로그램·펄…) |

**파일명 규칙:** `종류-모양-색상-번호.png` (영문 소문자·하이픈)
예) `rhinestone-heart-aurora-01.png`, `pearl-oval-white-01.png`, `resin-star-blue-01.png`

## 2. 새 이미지 추가하기

1. (선택) 작은 이미지는 먼저 업스케일합니다.

   ```
   pip install pillow numpy opencv-python-headless
   python tools/upscale_images.py 새이미지폴더 -o images
   ```
2. 이미지를 `images/` 에 넣고 파일명을 위 규칙대로 바꿉니다.
3. `python make_manifest.py` 실행 → 목록에 추가되고 썸네일이 만들어집니다.
4. `gallery-data.js` 에서 새 이미지의 `title` / `category` / `color` / `tags` 를 채웁니다.

> Python이 없다면 `images/` 와 `thumbs/` 에 파일을 직접 넣고, `gallery-data.js` 의 `images` 목록에
> `{ "file": "파일명.png", "title": "이름", "category": "종류", "color": "색상", "tags": ["태그"], "thumb": "파일명.webp" }` 를 추가해도 됩니다.

## 3. 내 컴퓨터에서 확인

- `index.html` 을 더블클릭하면 바로 열립니다. (이미지 보기·개별 다운로드 OK)
- **ZIP 다운로드는 웹 서버가 필요**해서, 확인하려면 폴더에서 아래를 실행하고 `http://localhost:8000` 으로 접속하세요.

  ```
  python -m http.server 8000
  ```

## 4. 무료로 배포하기

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

## 5. 웹에서 직접 업로드하기 (admin.html)

`https://내주소/admin.html` 에서 이미지를 첨부하고 제목·종류·색상·태그를 입력한 뒤 **반영하기**를 누르면,
이미지·썸네일·`gallery-data.js` 가 GitHub 저장소에 **한 번의 커밋**으로 올라갑니다. 커밋되면 호스팅이 자동으로 재배포하고, 그러면 사이트에 나타나요.

### 꼭 알아둘 점
- **별도 서버는 필요 없지만 GitHub 저장소가 필요해요.** 사이트 파일이 GitHub 저장소에 있어야 하고, 그 저장소를 **GitHub 연동 호스팅**이 배포해야 합니다.
  - 가능: GitHub Pages, Netlify(저장소 연결), Cloudflare Pages(저장소 연결)
  - **불가능: Netlify Drop처럼 폴더를 끌어다 놓는 방식.** 이 경우 커밋이 자동 배포로 이어지지 않아요.
- **관리자 전용**입니다. 토큰이 있는 사람만 올릴 수 있어요. 방문자가 직접 올리게 하려면 파일·DB를 저장할 백엔드(예: Supabase, Firebase)가 따로 필요해서, 이 방식으로는 안 됩니다.
- 반영까지 시간이 걸려요. GitHub Pages는 보통 1~2분 뒤에 사이트에 나타납니다.
- 업로드 화면에서는 **삭제·수정이 안 돼요.** 지우거나 고치려면 저장소에서 파일과 `gallery-data.js` 를 직접 수정하세요.
- 작은 이미지는 업스케일이 자동으로 되지 않습니다. 먼저 `tools/upscale_images.py` 로 키운 뒤 올리세요.

### 준비 (한 번만)
1. GitHub에 저장소를 만들고 이 폴더의 내용을 올립니다. (GitHub Pages: 저장소 Settings → Pages → Branch `main` / root)
2. 토큰을 만듭니다. GitHub → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** → Generate new token
   - Expiration: 만료일 지정 (예: 90일)
   - Repository access: **Only select repositories** → 이 저장소만 선택
   - Permissions → Repository permissions → **Contents: Read and write**
3. `admin.html` 을 열어 소유자, 저장소 이름, 브랜치, 토큰을 입력하고 **연결 확인**을 누릅니다.
   (index.html 이 저장소의 하위 폴더에 있다면 “사이트 폴더”에 그 경로를 적어요.)

### 사용
1. 이미지를 끌어다 놓기 → 카드마다 제목(필수)·종류·색상·태그·파일명 입력
   - 종류·색상은 기존 값이 자동완성으로 뜨고, 태그는 자주 쓰는 태그를 눌러 추가할 수 있어요.
   - 파일명은 영문 소문자·숫자·하이픈만 가능하고, 중복되면 안 돼요. (원본 파일명에서 자동 생성)
2. **반영하기** → 완료 후 “커밋 보기” 링크가 나타납니다.

### 보안
- 토큰은 브라우저에서 `api.github.com` 으로만 전송됩니다. “토큰 기억하기”는 개인 PC에서만 켜세요.
- 토큰이 유출됐다면 GitHub에서 즉시 폐기하세요. 권한을 저장소 하나·Contents 쓰기로만 준 이유가 이거예요.

## 운영 팁

- **업스케일 한계**: 이 사이트의 이미지는 AI 초해상도가 아니라 고전적 방식(알파 인식 확대)으로 키웠어요. 원본이 40px 안팎으로 아주 작았던 이미지는 선명도에 한계가 있으니, 가능하면 더 큰 원본으로 교체하는 게 가장 좋습니다.
- **용량**: 다운로드용 원본은 `images/`, 목록에는 작은 `thumbs/` 를 써서 첫 화면이 가볍게 열려요.
- **투명 배경**: 투명 PNG는 체크무늬 위에 보여서 투명 여부를 바로 알 수 있어요.
- **라이선스**: 무료 배포라도 "상업적 이용 가능 여부, 출처 표기 필요 여부"를 `license` 문구에 분명히 적어두면 분쟁을 줄일 수 있어요.
- **파일명**: 한글·공백이 있어도 동작하지만, 영문·숫자·하이픈(`cube-blue-01.png`)이 배포 시 가장 안전합니다.
- **ZIP 기능**은 브라우저에서 JSZip 라이브러리(cdnjs)를 불러와 동작합니다. 인터넷이 끊기면 ZIP만 안 되고 개별 다운로드는 그대로 됩니다.
