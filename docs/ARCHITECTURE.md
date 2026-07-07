# 아키텍처 상세

## 컴포넌트와 데이터 흐름

```
┌──────────────────────────── 브라우저 (서버 없음) ────────────────────────────┐
│                                                                             │
│  CodeMirror 에디터 (index.html)                                              │
│      │  사용자 VPython 코드                                                   │
│      ▼                                                                      │
│  main.js: 전처리                                                             │
│      - rate( → await rate(  (정규식, 줄 수 보존)                               │
│      - _new_run() 호출로 세대 증가                                             │
│      - renderer.reset()                                                     │
│      ▼                                                                      │
│  Pyodide (CPython 3.12 / WASM)  ← pyodide.runPythonAsync(code)              │
│      - vpython.py가 전역 네임스페이스에 로드되어 있음                              │
│      - print → main.js print() (setStdout/setStderr batched)                │
│      │  globalThis.vpw 호출 (JSON 문자열)                                     │
│      ▼                                                                      │
│  renderer.js (three.js r160)                                                │
│      - Scene/PerspectiveCamera/OrbitControls/조명                            │
│      - objects: Map<int, THREE.Mesh>                                        │
│      - requestAnimationFrame 루프 (Python과 독립적으로 항상 렌더)                │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 브리지 프로토콜 v1 (현재 구현)

Python은 `from js import vpw`로 아래 세 함수만 사용한다. **인자는 항상 JSON 문자열.**

| 함수 | 방향 | 계약 |
|---|---|---|
| `vpw.createObject(type, propsJson) -> int` | Py→JS | type: `"box" \| "sphere"`. 반환된 정수 id를 Python 객체가 보관 |
| `vpw.updateObject(id, propsJson)` | Py→JS | 변경된 속성만 담은 JSON. **모르는 id는 조용히 무시** (이전 세대 잔여 호출 대비) |
| `vpw.reset()` | JS 내부 | 새 Run 직전에 main.js가 호출. 모든 mesh 제거 + dispose |

인코딩 규칙:
- `vector(x,y,z)` → `[x, y, z]`
- 색 → `[r, g, b]` (각 0.0~1.0)
- `size` → 배열, `radius`/`opacity` → 숫자, `visible` → bool

## 실행 모델

**문제**: VPython 프로그램은 `while True: rate(100)` 블로킹 루프인데 브라우저 메인 스레드는 블로킹 불가.

**해법 (현재)**:
1. 실행 전 정규식으로 `rate(` → `await rate(` 치환 (이미 await가 붙은 경우 중복 방지 처리 있음).
2. `rate(n)`은 `asyncio.sleep(1/n)` — Pyodide의 WebLoop이 브라우저 이벤트 루프에 위임.
3. **세대 카운터**: 전역 `_generation`. Run마다 `_new_run()`이 +1. `rate()`는 sleep 후
   자신이 시작한 세대와 현재 세대가 다르면 `_Stopped` 예외를 던져 이전 루프를 종료.
   main.js는 `_Stopped`가 포함된 에러를 정상 종료로 취급.

**알려진 한계와 계획된 개선** (Phase 1/7에서 처리):
- 정규식 치환은 문자열/주석 안의 `rate(`도 바꾼다 → tokenize 기반 변환으로 교체 예정
  (Pyodide 안에서 Python `tokenize` 모듈로 NAME 토큰 `rate` + `(` 만 치환, 줄번호 보존).
- `rate()` 없는 무한루프(`while True: pass`)는 탭을 멈춘다 → 장기적으로 Web Worker 실행 검토
  (Phase 7 spec 참고).

## 속성 동기화 모델

- `_Object3D._known` 튜플에 있는 속성만 렌더러로 전송. `__setattr__` 가로채기 방식.
- 그 외 속성(velocity, mass 등)은 일반 Python 속성으로 자유롭게 허용 — VPython 관례.
- **현재 한계**: `ball.pos.x += 1`처럼 벡터 성분만 바꾸면 전송이 일어나지 않음.
  Phase 1에서 vector에 소유자 콜백을 붙여 해소 (spec 참고).

## 계획된 프로토콜 v2 — 업데이트 배칭 (Phase 1)

현재는 속성 대입 1회 = JS 호출 1회 + JSON 직렬화 1회. 객체 수백 개면 병목.

설계:
- Python 쪽에 전역 `_dirty: dict[int, dict[str, Any]]` 유지. `__setattr__`은 dirty에만 기록.
- `rate()`가 sleep 직전에 `vpw.applyUpdates(json.dumps(_dirty))` 1회 호출 후 dirty 비움.
  프로그램 정상 종료 시에도 1회 flush (main.js의 runPythonAsync 완료 후 `_flush()` 호출).
- `createObject`는 즉시 실행 유지 (id가 바로 필요하므로).
- 렌더러에 `applyUpdates(batchJson)` 추가: `{ "3": {"pos": [..]}, "7": {...} }` 형태.
- v1 함수(updateObject)는 하위 호환으로 유지.

## 계획된 axis/up 회전 모델 (Phase 1 — 모든 방향성 객체의 기반)

VPython 의미론:
- 객체의 로컬 X축이 `axis` 방향을 향한다. `up`은 로컬 Y축의 힌트.
- 직교 기저 계산: `x̂ = norm(axis)`, `ẑ = norm(x̂ × up)` (axis∥up이면 up 대체:
  x̂가 (0,1,0)과 평행하면 up=(0,0,1) 사용), `ŷ = ẑ × x̂`.
- three.js 적용: 기저 벡터 3개로 `Matrix4.makeBasis(x̂, ŷ, ẑ)` → `quaternion.setFromRotationMatrix`.
- **pos 의미가 객체마다 다름에 주의**:
  - 중심 기준: box, sphere, ellipsoid, ring, torus, compound
  - 시작점 기준(axis 방향으로 뻗음): cylinder, cone, arrow, pyramid, helix, text
  - 시작점 기준 객체는 지오메트리를 +X로 mag(axis)만큼 뻗도록 만들고 pos에 배치.
- **axis↔크기 결합**: box/ellipsoid는 `size.x == mag(axis)` 유지 (axis 대입 시 size.x 갱신,
  size.x 대입 시 axis 길이 갱신). cylinder류는 `length == mag(axis)`.

## 성능 예산

- 목표: 객체 1,000개가 `rate(100)`으로 움직일 때 60fps 유지 (Phase 9에서 벤치마크).
- 이를 위한 전제: 프로토콜 v2 배칭, 지오메트리 재사용(같은 type은 geometry 공유 고려).

## 의존성 버전 (변경 시 여기 갱신)

| 라이브러리 | 버전 | 로드 방식 |
|---|---|---|
| Pyodide | 0.26.4 | CDN script (jsdelivr) |
| three.js | 0.160.0 | CDN importmap (jsdelivr) |
| CodeMirror | 5.65.16 | CDN (cdnjs) |
