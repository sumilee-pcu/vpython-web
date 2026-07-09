# vpython-web

**Web VPython powered by real CPython** — 브라우저에서 진짜 CPython(Pyodide)으로 VPython 물리 시뮬레이션을 실행하는 웹 환경.

[GlowScript](https://www.glowscript.org/)와 달리 Python→JS 트랜스파일이 아니라 WebAssembly로 컴파일된 실제 CPython을 사용하므로, 장기적으로 numpy 등 표준 파이썬 생태계를 그대로 쓸 수 있는 것이 목표.

## 아키텍처

```
┌─────────────────────────── 브라우저 ───────────────────────────┐
│                                                                │
│  CodeMirror 에디터                                              │
│       │ (사용자 VPython 코드, rate() → await rate() 변환)        │
│       ▼                                                        │
│  Pyodide (CPython/WASM)                                        │
│    └─ src/vpython.py : VPython API 계층 (vector, box, sphere…) │
│            │ (JS 브리지: globalThis.vpw)                        │
│            ▼                                                   │
│  src/renderer.js : three.js/WebGL 렌더러 (GPU)                  │
└────────────────────────────────────────────────────────────────┘
```

- **실행 모델**: VPython의 `while True: rate(100)` 무한 루프는 실행 전에 `await rate(100)`으로 자동 변환되어, 매 프레임 브라우저에 제어권을 돌려준다. Run을 다시 누르면 세대 카운터가 올라가 이전 루프는 다음 `rate()`에서 종료된다.
- 서버 없음: 전부 정적 파일이라 GitHub Pages 등에 그대로 배포 가능.

## 실행 방법

Pyodide가 `vpython.py`를 fetch로 불러오기 때문에 로컬 웹서버가 필요하다 (`file://`로는 안 됨):

```bash
cd vpython-web
python -m http.server 8000
# 브라우저에서 http://localhost:8000 접속
```

첫 로딩 시 Pyodide(약 10MB) 다운로드로 수십 초 걸릴 수 있다 (이후 브라우저 캐시).

## 현재 지원하는 API

- `vector` (연산자, `mag`, `mag2`, `norm()`, `dot()`, `cross()`, 성분 수정 시 화면 자동 반영)
- `box`, `sphere` — pos, **axis/up (회전)**, size/radius, **length/height/width**,
  color, opacity, visible + velocity 등 자유 속성
- `cylinder` — pos(시작점), axis, radius, length 별칭, color, opacity, visible
- `color` 상수 (red, green, blue, yellow, orange, cyan, magenta, purple, white, black, gray())
- `rate(n)`, `print()` (하단 출력창), 에러 시 줄번호 표시 + 해당 줄 하이라이트
- 예제 라이브러리 드롭다운 (`examples/`의 물리 예제 30개 + 미리보기 로드)
- 마우스 드래그로 카메라 회전/줌 (OrbitControls)

### 알려진 제약

- 사용자 정의 함수 안에서 `rate()` 호출 불가 (top-level 루프에서만) — 함수 async화 미지원
- `rate()` 없는 무한루프는 탭을 멈춤 (Stop 버튼/Worker는 Phase 7)
- `scene` 객체는 스텁 (속성 설정은 조용히 무시됨 — Phase 4에서 구현)
- 백그라운드 탭에서는 브라우저 타이머 스로틀로 시뮬레이션이 느려짐 (웹 표준 동작)

## 로드맵

전체 구현 계획(9단계, VPython 전체 API 커버리지)은 [docs/ROADMAP.md](docs/ROADMAP.md) 참고.
