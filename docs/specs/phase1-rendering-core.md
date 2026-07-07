# Phase 1 스펙 — 렌더링 코어 보강

> 목적: 후속 모든 객체 구현의 기반. **이 단계를 건너뛰고 Phase 2를 시작하지 말 것** (재작업 발생).
> 설계 배경은 [ARCHITECTURE.md](../ARCHITECTURE.md)의 "계획된 ..." 절 참고.

## 1.1 axis / up 지원

**변경 파일**: `src/vpython.py`, `src/renderer.js`

- `_Object3D._known`에 `axis`, `up` 추가. 기본값: `axis=vector(1,0,0)`, `up=vector(0,1,0)`.
- 렌더러 `_applyProps`: axis/up 수신 시 ARCHITECTURE.md의 기저→쿼터니언 계산으로 `mesh.quaternion` 설정.
  axis와 up이 평행할 때의 폴백 처리 필수.
- axis↔크기 결합 (양방향):
  - box: `axis` 대입 → `size.x = mag(axis)` 자동 갱신. `size` 대입 → axis 방향 유지, 길이만 size.x로.
  - 파생 단축 속성 `length`(=size.x), `height`(=size.y), `width`(=size.z) 프로퍼티 추가.
- pos 의미(중심/시작점)는 객체별로 다름 — ARCHITECTURE.md 표 참고. Phase 1에서는 box/sphere만
  적용하면 되지만, 렌더러 구현은 "시작점 기준" 객체를 수용할 수 있게 지오메트리 오프셋 방식으로 만들 것
  (예: geometry.translate(0.5, 0, 0) 후 scale).

**수용 기준**:
```python
b = box(pos=vector(0,0,0), axis=vector(0,2,0), height=0.5)
# → 세로로 선 길이 2의 상자. b.size.x == 2 확인
b.length = 4        # → axis가 vector(0,4,0)이 됨
print(b.axis)       # <0, 4, 0>
```
브라우저에서 육안 확인 + `vpw.objects.get(id).quaternion`이 z축 90° 회전인지 preview_eval로 확인.

## 1.2 vector 성분 수정 동기화

**변경 파일**: `src/vpython.py`

설계:
- `vector`에 선택적 소유자 슬롯 추가: `_owner`(객체 참조), `_attr`(속성명). 기본 None.
- `vector.__setattr__` 재정의: x/y/z 대입 시 `_owner`가 있으면 `_owner._sync(_attr)` 호출.
  (`__slots__`에 `_owner`, `_attr` 추가. 성능 위해 owner 없을 때 오버헤드 최소화.)
- `_Object3D.__setattr__`에서 known 속성에 vector를 대입할 때: **복사본을 만들어** owner를 바인딩
  (VPython도 대입 시 복사 시맨틱. 하나의 vector를 두 객체에 대입해도 서로 간섭 없어야 함).
- `_Object3D.__getattr__`이 돌려주는 vector는 바인딩된 그 복사본이어야 함 (`b.pos.x = 1`이 동작하도록).
- 산술 연산 결과(`a + b` 등)는 owner 없는 새 vector.

**수용 기준**:
```python
ball = sphere()
ball.pos.x = 3              # 화면에서 즉시 이동
v = vector(1,1,1)
b1 = box(pos=v); b2 = box(pos=v)
b1.pos.x = 5                # b2는 움직이지 않아야 함
```

## 1.3 업데이트 배칭 (브리지 프로토콜 v2)

**변경 파일**: `src/vpython.py`, `src/renderer.js`, `src/main.js`

ARCHITECTURE.md "프로토콜 v2" 설계대로:
- Python: 전역 `_dirty` dict, `__setattr__`은 dirty 기록만. `_flush()`가 `vpw.applyUpdates(json)` 호출.
- `rate()` 진입 시 flush → sleep. 프로그램 종료 시 main.js가 `pyodide.runPython("_flush()")`.
- `createObject`는 동기 즉시 실행 유지. 단 생성 직전에 flush (생성 순서와 업데이트 순서 꼬임 방지).
- 렌더러: `applyUpdates(batchJson)` 추가. 기존 `updateObject`는 유지(하위 호환).

**수용 기준**: 기존 examples 전부 동작 + 아래 스트레스 테스트에서 프레임 유지(육안 30fps 이상):
```python
import random
balls = [sphere(radius=0.1, pos=vector(random.uniform(-5,5), random.uniform(-5,5), 0)) for _ in range(500)]
while True:
    rate(60)
    for b in balls:
        b.pos.x += random.uniform(-0.02, 0.02)
```

## 1.4 rate 변환 견고화 + 에러 줄번호

**변경 파일**: `src/main.js` (+ 변환 로직을 `src/vpython.py`의 `_transform(code)` 함수로 이동 권장)

- 정규식 치환 → Python `tokenize` 기반: NAME 토큰이 정확히 `rate`이고 다음 토큰이 `(`,
  그리고 앞 토큰이 `await`/`.`이 아닐 때만 치환. 문자열/주석 내 오탐 제거. **줄 수 보존.**
- 에러 표시: Python 트레이스백에서 Pyodide 내부 프레임(`/lib/python...`, `pyodide` 경로) 제거하고
  `<exec>` 프레임의 줄번호 + 해당 소스 줄을 출력창에 표시. 가능하면 CodeMirror 해당 줄 하이라이트.

**수용 기준**:
```python
s = "call rate(10) later"   # 문자열 안 → 변환되지 않아야 함
print(s)
x = 1/0                     # → 출력창에 "3행: ZeroDivisionError ..." 형태로 표시
```

## 완료 정의 (Phase 1 전체)

- [ ] 위 4개 항목의 수용 기준 전부 통과
- [ ] 기존 examples/ 2개가 수정 없이 동작
- [ ] ARCHITECTURE.md의 "계획된 ..." 절을 "현재 구현" 절로 옮겨 갱신
- [ ] ROADMAP.md 체크박스 갱신
