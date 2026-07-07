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
| `vpw.applyUpdates(batchJson)` | Py→JS | **v2 배칭 (주 경로)**: `{"3": {"pos": [..]}, "7": {...}}` — rate()/_flush()마다 변경분 일괄 전송. **모르는 id는 조용히 무시** (이전 세대 잔여 호출 대비) |
| `vpw.updateObject(id, propsJson)` | Py→JS | v1 단건 업데이트 (하위 호환용으로 유지, 현재 미사용) |
| `vpw.reset()` | JS 내부 | 새 Run 직전에 main.js가 호출. 모든 mesh 제거 + dispose |

인코딩 규칙:
- `vector(x,y,z)` → `[x, y, z]`
- 색 → `[r, g, b]` (각 0.0~1.0)
- `size` → 배열, `radius`/`opacity` → 숫자, `visible` → bool

## 실행 모델

**문제**: VPython 프로그램은 `while True: rate(100)` 블로킹 루프인데 브라우저 메인 스레드는 블로킹 불가.

**해법 (현재 구현)**:
1. 실행 전 `_transform(code)`(vpython.py, tokenize 기반)로 `rate(` 앞에 `await` 삽입.
   NAME 토큰 `rate` + 다음 토큰 `(` 일 때만 치환하므로 문자열/주석은 건드리지 않고,
   앞 토큰이 `await`/`def`/`.` 이면 건너뛴다. **줄 수 보존** (에러 줄번호 유지).
2. `rate(n)`은 `_flush()` 후 `asyncio.sleep(1/n)` — Pyodide의 WebLoop이 브라우저 이벤트 루프에 위임.
3. **세대 카운터**: 전역 `_generation`. Run마다 `_new_run()`이 +1. `rate()`는 sleep 후
   자신이 시작한 세대와 현재 세대가 다르면 `_Stopped` 예외를 던져 이전 루프를 종료.
   main.js는 `_Stopped`를 정상 종료로 취급하고, JS 쪽 `runCounter`로 상태 표시 경합을 정리.
   **Run 버튼은 실행 중에도 비활성화하지 않는다** — 무한 루프 프로그램의 유일한 재실행 수단.
4. 에러 표시: 트레이스백의 마지막 `File "<exec>", line N`에서 사용자 줄번호를 추출해
   출력창에 `N행: 에러` 형식으로 표시 + CodeMirror 해당 줄 하이라이트. 전체 트레이스백은 콘솔로.

**알려진 한계와 계획된 개선**:
- `rate()` 없는 무한루프(`while True: pass`)는 탭을 멈춘다 → 장기적으로 Web Worker 실행 검토
  (Phase 7 spec 참고).
- 사용자 정의 함수 안의 `rate()` 호출은 지원 안 됨 (함수가 async로 변환되지 않으므로 SyntaxError).
  전체 AST 변환(모든 함수를 async화)이 필요 — 필요성이 확인되면 착수.
- **브라우저 탭이 백그라운드면 타이머가 초당 1회로 스로틀**되어 시뮬레이션이 느려진다.
  모든 웹 애니메이션의 표준 동작 (GlowScript 동일). 헤드리스 테스트 시 유의.

## 속성 동기화 모델 (Phase 1에서 확정)

- `_Object3D._known`(frozenset)에 있는 속성만 렌더러로 전송. `__setattr__` 가로채기 방식.
- **동기화 속성도 실제 인스턴스 속성으로 저장한다** — `b.pos` 읽기가 `__getattr__` 예외
  경로를 타지 않게 하기 위함. dict 저장 방식 대비 스트레스 테스트에서 틱당 33ms → 18ms.
  `_sync_keys` 튜플이 객체별 동기화 속성 목록을 보관 (생성 시 인코딩에 사용).
- **vector 소유자 바인딩**: known 속성에 vector를 대입하면 복사본을 만들어 `_owner/_attr`을
  바인딩. 성분 수정(`b.pos.x += 1`)이 `owner._mark_dirty()`를 호출해 화면에 반영된다.
  대입은 복사 시맨틱 — 같은 vector를 두 객체에 대입해도 서로 간섭하지 않는다.
- 그 외 속성(velocity, mass 등)은 일반 Python 속성으로 자유롭게 허용 — VPython 관례.
- **배칭**: `__setattr__`/성분 수정은 전역 `_dirty: dict[id, dict[prop, 값참조]]`에 기록만 하고,
  `rate()`/`_flush()`가 `vpw.applyUpdates(json)` 1회로 일괄 전송. 값은 flush 시점에 인코딩
  (같은 속성을 여러 번 바꿔도 마지막 값만 1회 인코딩). `createObject` 직전에도 flush
  (생성/업데이트 순서 보존). 프로그램 정상 종료 시 main.js가 `_flush()` 1회 호출.
- box 계열은 `size.x == mag(axis)` 결합을 `_mark_dirty`에서 유지 (`_coupling` 플래그로
  재진입 차단). `length/height/width`는 size 성분의 별칭.

## axis/up 회전 모델 (구현됨 — 모든 방향성 객체의 기반)

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
- **현재 측정치** (2026-07, RTX 4060): 구 500개 × 성분 갱신 2회/틱 + flush = **18.0ms/틱**
  (~55fps 상당). 분해: random.uniform 240k회 ≈ 0.4s/120틱, 우리 계층 갱신 오버헤드
  ≈ 4µs/회, flush(JSON 직렬화+파싱+적용) ≈ 잔여 대부분.
- 남은 최적화 레버 (Phase 9): flush의 JSON 경로를 `pyodide.ffi.to_js` 또는 평탄 배열로 교체,
  같은 type의 geometry 공유, 대량 동일 객체는 InstancedMesh.

## 의존성 버전 (변경 시 여기 갱신)

| 라이브러리 | 버전 | 로드 방식 |
|---|---|---|
| Pyodide | 0.26.4 | CDN script (jsdelivr) |
| three.js | 0.160.0 | CDN importmap (jsdelivr) |
| CodeMirror | 5.65.16 | CDN (cdnjs) |
