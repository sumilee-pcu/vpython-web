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

## 현재 지원하는 API (MVP)

- `vector` (연산자, `mag`, `mag2`, `norm()`, `dot()`, `cross()`)
- `box`, `sphere` (pos, size/radius, color, opacity, visible + velocity 등 자유 속성)
- `color` 상수 (red, green, blue, yellow, orange, cyan, magenta, purple, white, black, gray())
- `rate(n)`, `print()` (하단 출력창)
- 마우스 드래그로 카메라 회전/줌 (OrbitControls)

### 알려진 제약

- `ball.pos.x += 1`처럼 벡터의 **성분만 수정하면 화면에 반영되지 않음** — `ball.pos = ...`로 재대입해야 동기화됨 (단, `velocity`처럼 렌더링과 무관한 자유 속성은 상관없음)
- `scene` 객체는 스텁 (속성 설정은 조용히 무시됨)

## 로드맵

전체 구현 계획(9단계, VPython 전체 API 커버리지)은 [docs/ROADMAP.md](docs/ROADMAP.md) 참고.
