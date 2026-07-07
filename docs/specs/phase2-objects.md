# Phase 2 스펙 — 3D 객체 전체 구현

> 전제: Phase 1 완료 (axis/up, 배칭). 각 객체는 `_Object3D` 상속 + renderer.js에 지오메트리 추가의 반복 작업.
> ⚠️ 기본값은 구현 직전에 공식 문서로 재확인: `https://www.glowscript.org/docs/VPythonDocs/<객체명>.html`

## 공통 패턴

새 객체 1개 추가 절차:
1. `vpython.py`: 팩토리 함수 + defaults dict (+ 객체 고유 `_known` 속성 있으면 클래스 분리)
2. `renderer.js` `createObject`: three.js 지오메트리 매핑 추가
3. `_applyProps`: 고유 속성 처리 추가
4. `examples/`에 그 객체를 쓰는 최소 예제 추가 (회귀 테스트 겸용)

## 2.1 프리미티브 (pos=시작점, axis 방향으로 뻗는 그룹)

| 객체 | 주요 속성 (기본값은 문서 확인) | three.js 매핑 | 비고 |
|---|---|---|---|
| `cylinder` | pos, axis, radius | CylinderGeometry — 기본이 Y축 방향이므로 +X로 눕히고 시작점 오프셋 | length=mag(axis) |
| `cone` | pos, axis, radius | ConeGeometry (동일한 축 보정) | 꼭짓점이 axis 끝 |
| `arrow` | pos, axis, shaftwidth, headwidth, headlength, round | 샤프트(Box 또는 Cylinder)+머리(Cone)를 Group으로 | 기본 shaftwidth=0.1·mag(axis), head는 shaftwidth 비례 — **문서 확인** |
| `pyramid` | pos, size, axis | 사각뿔 BufferGeometry 직접 작성 | size.x가 axis 방향 |
| `helix` | pos, axis, radius, coils, thickness | TubeGeometry + 나선 Curve3 | coils 기본 5 — 문서 확인. axis/radius 변경 시 지오메트리 재생성 필요 |

## 2.2 프리미티브 (pos=중심 그룹)

| 객체 | 주요 속성 | three.js 매핑 | 비고 |
|---|---|---|---|
| `ellipsoid` | pos, axis, length, height, width | SphereGeometry + 비균등 scale | box와 같은 axis↔length 결합 |
| `ring` | pos, axis, radius, thickness | TorusGeometry (axis가 링의 법선) | thickness 기본값 문서 확인 |
| `torus` | ring과 동일 (GlowScript 별칭 여부 문서 확인) | TorusGeometry | |

## 2.3 동적/복합 객체 (전용 브리지 함수 필요)

**curve** — 궤적/그래프의 핵심. 별도 클래스로:
```python
c = curve(color=color.red, radius=0.05)   # radius=선 굵기(월드 단위)
c.append(vector(0,0,0))                    # 또는 c.append(pos=..., color=...)
c.modify(i, pos=...); c.clear(); c.npoints
```
- 렌더러: 굵기 있으면 TubeGeometry 재생성(비싸므로 점 추가 배칭), 없으면 Line + LineBasicMaterial.
- 브리지 확장: `vpw.curveOp(id, opJson)` — `{op:"append"|"modify"|"clear", ...}`.

**points** — curve와 유사하되 THREE.Points + PointsMaterial. `radius`는 픽셀 크기.

**label** — 3D 위치에 고정된 2D 오버레이:
```python
label(pos=vector(0,1,0), text='Hello', height=16, box=True, opacity=0.66, font='sans')
```
- 구현: `#canvas-host` 위에 absolute div. 렌더 루프에서 매 프레임 pos를 화면 좌표로 투영해 이동.
- 렌더러에 오버레이 관리 배열 추가. reset() 시 함께 제거.

**text** — 3D 입체 글자. three.js `TextGeometry` + FontLoader (helvetiker 폰트 CDN).
  속성: text, pos, axis, height, depth, color. 폰트 로딩이 비동기이므로 생성 시 placeholder → 로드 후 교체.

**compound** — `compound([obj1, obj2, ...])`: 자식 mesh들을 THREE.Group으로 묶고 원본 id들은 그룹에 흡수.
  이후 pos/axis/size는 그룹에 적용. 자식의 개별 수정은 불가(VPython과 동일).

**clone** — `obj.clone(pos=...)`: Python 쪽에서 현재 props를 복사해 새 createObject. 지오메트리 공유는 렌더러 최적화로.

## 2.4 자취/부착 (attach)

- `make_trail=True` 생성 인자 + `attach_trail(obj, retain=N, radius=, pps=)`:
  내부적으로 curve를 만들고, **배칭 flush 시점**(rate)마다 obj.pos를 append. retain 초과 시 앞점 제거.
- `attach_arrow(obj, "velocity", scale=1)`: flush마다 obj.velocity를 읽어 화살표 갱신. Phase 5 이후로 미뤄도 됨.

## 2.5 재질/외형 공통 속성

- `texture`: `_known`에 추가. 값은 URL 문자열. `textures.wood` 등 내장 세트는
  `assets/textures/`에 CC0 이미지로 자체 번들 (GlowScript 이미지 무단 사용 금지, 출처 기록).
  렌더러: TextureLoader 캐시 맵 유지.
- `shininess`(0~1) → three.js roughness로 역매핑(대략 `roughness = 1 - shininess`), `emissive`(bool) → material.emissive에 color 적용.
- `obj.rotate(angle=, axis=, origin=)`: Python 쪽에서 axis/up/pos를 로드리게스 회전으로 갱신 (Phase 3의 rotate 재사용). 렌더러 변경 불필요.
- `obj.visible`, `obj.pos` 등은 이미 있음. `obj.delete()`? — VPython은 `obj.visible=False` + 참조 해제가 관례. `vpw.deleteObject(id)` 브리지 추가 권장.

## 완료 정의

- [ ] 위 객체 전부 + examples/에 데모 추가 (spring_helix.py, projectile_arrow.py 권장)
- [ ] GlowScript 문서의 각 객체 페이지와 기본값 대조 완료
- [ ] 기존 예제 회귀 통과, ROADMAP/ARCHITECTURE 갱신
