# vpython-web 전체 구현 로드맵

목표: GlowScript / VPython 7 공식 API를 브라우저(Pyodide + three.js)에서 완전 호환으로 구현.
기준 문서: https://www.glowscript.org/docs/VPythonDocs/index.html

> **작업자/AI 온보딩**: 먼저 [/CLAUDE.md](../CLAUDE.md)를 읽을 것. 이 로드맵의 체크박스가
> 진행 상태의 단일 진실 원천이고, 각 단계의 상세 구현 스펙(시그니처·기본값·설계·수용 기준)은
> `docs/specs/phaseN-*.md`에 있다. **스펙을 읽지 않고 구현을 시작하지 말 것.**

| 단계 | 상세 스펙 |
|---|---|
| Phase 1 | [specs/phase1-rendering-core.md](specs/phase1-rendering-core.md) |
| Phase 2 | [specs/phase2-objects.md](specs/phase2-objects.md) |
| Phase 3 | [specs/phase3-vector-math.md](specs/phase3-vector-math.md) |
| Phase 4 | [specs/phase4-scene.md](specs/phase4-scene.md) |
| Phase 5 | [specs/phase5-events.md](specs/phase5-events.md) |
| Phase 6 | [specs/phase6-graphs-widgets.md](specs/phase6-graphs-widgets.md) |
| Phase 7 | [specs/phase7-python-ecosystem.md](specs/phase7-python-ecosystem.md) |
| Phase 8 | [specs/phase8-platform.md](specs/phase8-platform.md) |
| Phase 9 | [specs/phase9-quality.md](specs/phase9-quality.md) |

범례: ✅ 완료 / 🔜 다음 작업 / 예상 공수는 1인 기준.

---

## Phase 0 — MVP (완료)

- ✅ Pyodide(CPython/WASM) 실행 파이프라인
- ✅ `rate()` → `await rate()` 자동 변환, 재실행 시 이전 루프 중단(세대 카운터)
- ✅ `vector` (연산자, mag, mag2, norm, dot, cross)
- ✅ `box`, `sphere` (pos, size/radius, color, opacity, visible)
- ✅ `color` 상수, `rate()`, `print()` 출력창
- ✅ three.js 렌더러 + OrbitControls + 조명

---

## Phase 1 — 렌더링 코어 보강 (모든 후속 작업의 기반) — 약 1주

지금 구조의 한계를 먼저 풀어야 나머지 객체 추가가 쉬워진다.

- [ ] **`axis` / `up` 지원** — VPython 객체 방향의 핵심 개념. axis 벡터 → 쿼터니언 회전 변환.
      box/cylinder/arrow/cone 전부 이것에 의존. 렌더러에 회전 적용 로직 추가
- [ ] **vector 성분 수정 동기화** — `ball.pos.x += 1`이 화면에 반영되도록
      vector에 소유자 콜백(owner/attr) 연결. 현재 알려진 제약 1번 해소
- [ ] **업데이트 배칭** — 현재 속성 1개당 JSON 1회 전송. 프레임당 변경분을 모아
      한 번에 flush (rate()에서 일괄 전송). 객체 수백 개 시뮬레이션 대비 필수
- [ ] **에러 트레이스백 줄번호 보정** — rate 변환이 코드를 바꿔도 사용자 코드 기준
      줄번호로 에러 표시 (변환을 줄 단위 보존 방식으로)

## Phase 2 — 3D 객체 전체 구현 — 약 2~3주

기하학적 프리미티브 (Phase 1의 axis 기반 위에서):

- [ ] `cylinder` (pos, axis, radius)
- [ ] `arrow` (pos, axis, shaftwidth, headwidth, headlength)
- [ ] `cone`, `pyramid`
- [ ] `ellipsoid` (length, height, width)
- [ ] `ring` (thickness), `torus`
- [ ] `helix` (coils, thickness) — 스프링 시뮬레이션 필수 요소

동적/복합 객체:

- [ ] `curve` (append, modify, clear — 동적 정점 관리, 궤적 그리기)
- [ ] `points` (점 구름)
- [ ] `label` (2D 오버레이 텍스트: text, height, box, line — CSS 오버레이로 구현)
- [ ] `text` (3D 입체 텍스트 — three.js TextGeometry)
- [ ] `compound` (여러 객체 묶기), `obj.clone()`
- [ ] `attach_trail` / `make_trail=True` (자취), `attach_arrow` (벡터 화살표 부착)

공통 재질/외형 속성:

- [ ] `texture` (three.js TextureLoader, textures.* 내장 세트)
- [ ] `shininess`, `emissive`
- [ ] `obj.rotate(angle, axis, origin)` 메서드

## Phase 3 — 벡터/수학 함수 완성 — 약 3일

- [ ] `rotate(v, angle, axis)` / `v.rotate()`
- [ ] `proj(a, b)`, `comp(a, b)`, `hat(v)`, `diff_angle(a, b)`
- [ ] `v.equals()`, vector 해시/복사 시맨틱 VPython과 일치시키기
- [ ] GlowScript 내장 유틸: `arange`, `random` 계열 (Pyodide는 표준 random이 이미 있으므로 alias만)

## Phase 4 — scene(canvas) 구현 — 약 1~2주

- [ ] 카메라: `scene.forward`, `scene.center`, `scene.range`, `scene.fov`,
      `scene.camera.pos/axis`, `scene.camera.follow(obj)`
- [ ] `scene.autoscale` (객체가 화면 밖으로 나가면 자동 줌아웃 — VPython 기본 동작)
- [ ] `scene.background`, `scene.ambient`
- [ ] 조명 제어: `distant_light()`, `local_light()`, `scene.lights` 교체
- [ ] `scene.title`, `scene.caption` (HTML 영역), `scene.width/height`
- [ ] `scene.visible`, `scene.delete()`, **다중 canvas** 지원
- [ ] `sleep(t)`, `scene.pause()`, `scene.waitfor('click' 등)`

## Phase 5 — 이벤트/입력 — 약 1주

- [ ] `scene.bind('click' | 'mousedown' | 'mousemove' | 'mouseup' | 'keydown' | 'keyup', handler)`
      — Python 콜백을 JS 이벤트에 연결 (Pyodide proxy 수명 관리 주의)
- [ ] `scene.mouse.pos` (마우스 위치의 3D 투영), `scene.mouse.pick()` (객체 피킹 — raycaster)
- [ ] `keysdown()` (현재 눌린 키 목록)
- [ ] 이벤트 핸들러도 세대 카운터로 정리 (재실행 시 이전 핸들러 해제)

## Phase 6 — 그래프 & UI 위젯 — 약 1~2주

그래프 (자체 canvas 2D 또는 Plotly.js):

- [ ] `graph` (xtitle, ytitle, xmin/xmax, scroll)
- [ ] `gcurve`, `gdots`, `gvbars`, `ghbars` (plot 메서드, 실시간 갱신)

UI 위젯 (scene.caption 영역에 HTML로):

- [ ] `button`, `slider`, `menu`, `checkbox`, `radio`
- [ ] `wtext`, `winput`

## Phase 7 — 파이썬 생태계 활용 (이 프로젝트의 차별점) — 약 3일

- [ ] **numpy 자동 로드** — 코드에서 import 감지 → `pyodide.loadPackagesFromImports()`
      (GlowScript는 불가능한 기능. scipy, sympy도 동일 메커니즘)
- [ ] `math`, `random` 등 표준 모듈 그대로 사용 확인 및 문서화
- [ ] Stop 버튼 (rate 없는 무한루프 대비 — 장기적으로 Web Worker 실행 검토)

## Phase 8 — IDE/플랫폼 기능 — 약 2~3주

- [ ] 예제 갤러리 (examples/ 폴더를 드롭다운으로 로드)
- [ ] 자동 저장 (localStorage) + 파일 열기/저장
- [ ] **단일 HTML로 내보내기** (GlowScript의 export 기능 대응)
- [ ] URL 공유 (코드를 URL 해시에 압축 인코딩 — 서버 없이 공유 가능)
- [ ] GitHub Pages 자동 배포 (Actions)
- [ ] **클라우드 저장** (Supabase): 구글 로그인, 내 프로그램 CRUD, 폴더,
      공개/비공개, 공유 링크 — RLS 정책 설계 포함
- [ ] Monaco 전환 + VPython API 자동완성 (선택)

## Phase 9 — 호환성 검증 & 품질 — 상시

- [ ] **GlowScript 공식 예제 호환성 스위트** — glowscript.org의 대표 예제
      (Bounce, Binary star, Rug, Stonehenge 등)를 그대로 붙여넣어 통과하는지 회귀 테스트
- [ ] vector/수학 함수 단위 테스트 (pytest를 Pyodide 안에서 실행)
- [ ] 성능 벤치마크: 객체 1,000개 + rate(100) 유지 여부
- [ ] 모바일/태블릿 터치 대응
- [ ] 문서화: API 레퍼런스, GlowScript와의 차이점 페이지

---

## 권장 진행 순서와 이유

1. **Phase 1이 최우선** — axis/성분동기화/배칭은 뒤로 미룰수록 재작업 비용이 커지는 구조 변경.
2. Phase 2~3까지 되면 GlowScript 물리 예제의 **~80%가 그대로 실행**된다 (교육용으로 쓸 만한 시점).
3. Phase 4~5까지가 "VPython 호환"이라 부를 수 있는 선.
4. Phase 6은 물리 수업(그래프)용, Phase 7~8은 서비스화 단계 — 목적에 따라 순서 조정 가능.

총 예상 공수: 풀타임 1인 기준 **약 2.5~4개월** (Phase 9 제외).
GlowScript 문법 100% 호환이 목표가 아니라 "주요 물리 시뮬레이션이 도는 것"이 목표라면 Phase 1~3 (약 1개월)로 충분.
