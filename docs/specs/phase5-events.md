# Phase 5 스펙 — 이벤트/입력

> 변경 파일: `src/vpython.py`, `src/renderer.js`, `src/main.js`
> 문서: https://www.glowscript.org/docs/VPythonDocs/mouse.html, keyboard.html

## 5.1 scene.bind / unbind

```python
def on_click(ev):
    print(ev.pos)          # 클릭 지점의 3D 좌표
scene.bind('click', on_click)
scene.unbind('click', on_click)
```

- 지원 이벤트: `click`, `mousedown`, `mouseup`, `mousemove`, `keydown`, `keyup`.
  공백 구분 다중 등록 지원: `scene.bind('mousedown mouseup', f)`.
- **Pyodide proxy 수명 관리 (이 단계의 최대 함정)**:
  - Python 콜백을 JS에 넘길 때 `pyodide.ffi.create_proxy(f)` 사용, unbind/세대 교체 시 `proxy.destroy()`.
  - 권장 구조: JS에 Python 콜백을 직접 걸지 말고, **JS는 이벤트를 큐에 쌓고
    Python 쪽 flush(rate) 시점에 큐를 비우며 콜백 호출** — proxy 문제 자체를 회피하고
    콜백이 동기 Python으로 돌므로 세대 관리도 단순해짐. 단 이벤트 지연이 1 rate 틱 생김.
    GlowScript도 유사한 지연이 있으므로 허용. (마우스무브 등 고빈도 이벤트는 큐에서 최신만 유지.)
- `_new_run()` 시 모든 바인딩/큐 초기화 (CLAUDE.md 불변 규칙 2).

## 5.2 이벤트 객체

콜백 인자 `ev`의 속성 (VPython 호환):

| 속성 | 마우스 이벤트 | 키 이벤트 |
|---|---|---|
| `ev.pos` | 3D 투영 좌표 (5.3) | — |
| `ev.event` | 'click' 등 이벤트명 | 동일 |
| `ev.which` | 1=왼쪽 버튼 | — |
| `ev.key` | — | 'a', 'up', 'shift' 등 GlowScript 이름 규칙 (문서 확인) |
| `ev.ctrl/alt/shift` | bool | bool |

## 5.3 scene.mouse

- `scene.mouse.pos` — 마우스 위치를 **scene.center를 지나고 카메라 시선에 수직인 평면**에
  투영한 3D 좌표 (VPython 정의). three.js Raycaster + Plane으로 계산. 동기 조회이므로
  렌더러가 마지막 마우스 좌표를 항상 보관.
- `scene.mouse.pick()` — Raycaster로 맨 앞 객체 반환 (renderer id → Python 객체 역매핑 테이블 필요.
  `vpython.py`에 `_objects_by_id: dict[int, _Object3D]` 유지 — weakref 권장).
- `scene.mouse.ray`, `scene.mouse.project(normal=, point=)` — 후순위.

## 5.4 keysdown()

- 현재 눌린 키 이름 리스트. JS 쪽 keydown/keyup으로 Set 유지, 동기 조회.
- 주의: 캔버스가 아니라 window에 리스너 (에디터에 포커스 있을 때는 무시하도록 포커스 확인).

## 5.5 scene.waitfor / pause 연동

Phase 4에서 시그니처 정의한 것을 이벤트 큐 위에 구현:
`waitfor`는 해당 이벤트가 큐에 들어올 때까지 `asyncio.sleep(1/60)` 폴링 (세대 확인 포함).

## 완료 정의

- [ ] 5.1~5.4 구현 + examples/click_to_place.py (클릭 위치에 공 생성), drag_demo.py
- [ ] Run 재실행 시 이전 핸들러가 절대 호출되지 않음을 확인 (세대 테스트)
- [ ] 기존 예제 회귀 통과, ROADMAP 갱신
