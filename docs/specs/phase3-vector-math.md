# Phase 3 스펙 — 벡터/수학 함수 완성

> 변경 파일: `src/vpython.py`만. 렌더러 변경 없음. 전부 순수 함수라 단위 테스트 대상.

## 3.1 회전

```python
rotate(v, angle=a, axis=k)   # 함수형
v.rotate(angle=a, axis=k)    # 메서드형 — 새 vector 반환 (원본 불변, VPython 7 시맨틱 확인)
```
로드리게스 공식: `v' = v·cosθ + (k̂×v)·sinθ + k̂·(k̂·v)(1−cosθ)`. axis 기본값 `vector(0,0,1)`.

## 3.2 투영/성분/방향

| 함수 | 정의 |
|---|---|
| `hat(v)` | `v/mag(v)`, 영벡터면 `vector(0,0,0)` (`norm`과 동일, 별칭) |
| `proj(a, b)` | `dot(a, hat(b)) * hat(b)` — a의 b방향 벡터 성분 |
| `comp(a, b)` | `dot(a, hat(b))` — 스칼라 성분 |
| `diff_angle(a, b)` | `acos(clamp(dot(hat(a), hat(b)), -1, 1))` — 라디안. clamp 필수(부동소수점) |
| `a.equals(b)` | 성분 일치 여부 |

## 3.3 vector 시맨틱 정리

- `vector(v)` 복사 생성자 지원 (인자 1개가 vector면 복사).
- `-v`, `v1 == v2`, `str(v)` → `<x, y, z>` 형식 (이미 구현됨 — 확인만).
- `v.mag = 5` 대입 지원 (방향 유지, 크기 변경) — VPython은 mag/mag2에 setter가 있음.
  Phase 1의 owner 콜백과 충돌하지 않게 구현.
- `v.hat` 프로퍼티 (getter: 단위벡터 / setter: 방향만 교체) — 문서 확인 후 구현.

## 3.4 GlowScript 내장 유틸

- `arange(start, stop, step)` — range의 float 버전. numpy 없이 순수 파이썬 제너레이터로.
- `random()`, `sqrt`, `sin` 등: Pyodide는 표준 `math`/`random`이 이미 있으므로
  **GlowScript처럼 전역에 자동 노출할지 결정 필요** → 방침: `vpython.py` 상단에서
  `from math import sin, cos, tan, asin, acos, atan, atan2, sqrt, exp, log, pow, floor, ceil` +
  `from random import random, uniform, randint` 를 전역에 노출 (GlowScript 코드 호환 목적).
- `pi` 이미 노출됨.

## 3.5 단위 테스트 (이 단계에서 테스트 기반 도입)

`tests/test_vector.py` 작성 — Pyodide 없이 로컬 CPython으로도 돌 수 있게
`vpython.py`의 `from js import vpw`를 지연/모킹 가능하게 분리:
```
src/vpython.py  →  수학 부분을 src/vpmath.py로 분리, vpython.py가 import
tests/test_vector.py  →  로컬에서 `python -m pytest tests/` 로 실행
```
케이스: 연산자 전부, mag/norm 영벡터, rotate 90°/360°, proj/comp 직교·평행, diff_angle 경계(0, π).

## 완료 정의

- [ ] 3.1~3.4 구현, pytest 통과 (`python -m pytest tests/`)
- [ ] `examples/`의 기존 예제 회귀 통과
- [ ] ROADMAP 갱신
