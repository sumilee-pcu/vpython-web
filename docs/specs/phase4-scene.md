# Phase 4 스펙 — scene(canvas) 구현

> 현재 `scene`은 모든 대입을 무시하는 스텁. 이를 실제 canvas 객체로 교체한다.
> 변경 파일: `src/vpython.py`, `src/renderer.js`, `src/main.js`(다중 canvas 시 레이아웃)
> 기본값 재확인: https://www.glowscript.org/docs/VPythonDocs/canvas.html

## 4.1 브리지 확장

`vpw.sceneOp(canvasId, opJson)` 추가 — scene 속성 변경/조회용.
조회가 필요한 속성(mouse.pos 등)은 JS→Py 반환값이 필요하므로 동기 호출로 설계.

## 4.2 카메라 계열

| 속성/메서드 | 의미 | three.js 매핑 |
|---|---|---|
| `scene.forward` | 시선 방향 단위벡터 (기본 `vector(0,0,-1)`) | camera 위치/타겟 재계산 |
| `scene.center` | 바라보는 점 (기본 원점) | controls.target |
| `scene.range` | center에서 화면 세로 반경(월드 단위) | camera 거리 = range / tan(fov/2) |
| `scene.fov` | 시야각 라디안 (기본값 문서 확인, 통상 π/3) | camera.fov (도 단위 변환) |
| `scene.up` | 카메라 up (기본 `vector(0,1,0)`) | camera.up |
| `scene.camera.pos` / `scene.camera.axis` | 저수준 카메라 제어 | 직접 설정. forward/center와 상호 갱신 규칙 문서 확인 |
| `scene.camera.follow(obj)` | 객체 추적 | 렌더 루프에서 매 프레임 controls.target = obj.pos. `follow(None)` 해제 |

**주의**: OrbitControls의 사용자 조작과 프로그램 제어가 충돌한다.
방침: 프로그램이 카메라 속성을 대입하면 그 값을 적용하되 OrbitControls는 계속 활성
(GlowScript도 사용자 드래그 허용). controls.target/카메라 위치를 직접 갱신하는 방식으로 구현.

## 4.3 autoscale

- `scene.autoscale = True`(기본): 렌더 루프에서 전체 객체의 바운딩 구를 계산해
  화면을 벗어나면 range를 키움 (**줄이지는 않음** — VPython 동작).
- 사용자가 `scene.range`를 대입하면 autoscale 자동 해제 (VPython 동작. 문서 확인).
- 성능: 바운딩 계산은 매 프레임이 아니라 배칭 flush 시점에만.
- 구현 후 examples의 하드코딩된 카메라 위치를 기본값으로 되돌려 자연스럽게 보이는지 확인.

## 4.4 배경/조명

- `scene.background = color.white` → scene.background 색.
- `scene.ambient = color.gray(0.2)` (기본값 문서 확인) → AmbientLight 강도/색.
- `distant_light(direction=, color=)`, `local_light(pos=, color=)` → Directional/PointLight 추가.
- `scene.lights` — 기본 조명 리스트. `scene.lights = []`로 전부 끄기 지원.
  렌더러의 하드코딩 조명을 이 구조로 재편.

## 4.5 텍스트 영역/크기

- `scene.title`, `scene.caption` — canvas 위/아래 HTML 영역. `\n` 처리.
  `scene.append_to_title/caption` 도. **Phase 6 위젯이 이 영역에 들어가므로 컨테이너 구조를 미리 잡을 것.**
- `scene.width`, `scene.height` (기본 640×400. 현재는 패널 크기에 맞춤 — 대입 시에만 고정 크기로 전환).
- `scene.visible`, `scene.delete()`.

## 4.6 시간/대기 함수

- `sleep(t)` → `await asyncio.sleep(t)` + rate와 동일한 세대 확인. rate 변환기에 `sleep`도 추가.
- `scene.pause(prompt="")` → 화면에 ▶ 오버레이 표시, 클릭까지 대기 (Promise → asyncio Future).
- `scene.waitfor('click')` 등 → Phase 5 이벤트 기반. 시그니처만 여기 정의:
  `ev = scene.waitfor('click keydown')` (공백 구분 다중 이벤트, 발생한 이벤트 객체 반환).
- 전부 await 자동 변환 대상에 등록 (`rate`, `sleep`, `scene.pause`, `scene.waitfor`,
  `get_library` 등 — 변환기를 이름 목록 기반으로 일반화).

## 4.7 다중 canvas

- `c2 = canvas(width=, height=, ...)` — 새 렌더러 인스턴스 + DOM 컨테이너 추가.
- 전역 팩토리(box 등)는 "현재 canvas"(마지막 생성 또는 `c2.select()`)에 붙음. `canvas.get_selected()`.
- 객체 생성 인자 `canvas=c2` 지원.
- 렌더러를 클래스 인스턴스 여러 개로 — 현재 구조가 이미 클래스라 확장 용이.
  브리지 함수에 canvasId 인자 추가 필요 (v2 프로토콜에 반영).

## 완료 정의

- [ ] 4.1~4.6 구현 (4.7 다중 canvas는 후순위 가능 — ROADMAP에 별도 체크)
- [ ] examples에 camera_follow.py, lights_demo.py 추가
- [ ] 기존 예제 회귀 통과, ROADMAP/ARCHITECTURE 갱신
