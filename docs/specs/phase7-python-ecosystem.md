# Phase 7 스펙 — 파이썬 생태계 활용 (이 프로젝트의 차별점)

> GlowScript가 못 하는 것들. 변경 파일: `src/main.js` 중심.

## 7.1 numpy/scipy 자동 로드

- Run 시 `pyodide.loadPackagesFromImports(code)`를 실행 전에 호출 — 코드의 import문을 분석해
  필요한 Pyodide 패키지(numpy, scipy, sympy, pandas...)를 자동 다운로드.
- 상태 표시: "numpy 로딩 중..." (최초 1회만, 이후 캐시).
- Pyodide 배포에 없는 순수 파이썬 패키지는 micropip 폴백:
  `await micropip.install(name)` — 실패 시 명확한 에러 메시지.
- examples/numpy_wave.py 추가 (numpy로 파동 계산 → curve로 시각화) — **데모 가치가 큰 예제.**

## 7.2 Stop 버튼

- Run 버튼 옆 ■ Stop: `_new_run()`만 호출 (다음 rate에서 루프 종료). 실행 중일 때만 활성화.
- 한계 명시: `rate()` 없는 순수 CPU 루프는 이 방법으로 못 멈춤 (메인 스레드 점유).
  → UI에 "5초 이상 응답 없음" 감지는 불가능(같은 스레드)하므로, README에 알려진 제약으로 기록.

## 7.3 Web Worker 실행 (설계 검토 문서 — 구현은 선택)

근본 해결책. 착수 전 이 절을 별도 설계 문서로 확장할 것. 요점:
- Pyodide를 Worker에서 실행, 렌더러는 메인 스레드 유지.
- 브리지가 동기 호출 불가능해짐 → 프로토콜 v2 배칭이 사실상 메시지 패싱이므로 궁합은 좋음.
  단 `createObject`의 동기 id 반환, `scene.mouse.pos` 동기 조회가 문제:
  - id는 Python 쪽에서 발급(카운터)하면 동기 불필요.
  - 동기 조회는 SharedArrayBuffer + Atomics.wait 필요 → GitHub Pages에서 COOP/COEP 헤더 제약 확인 필수.
- Stop은 worker.terminate() + 재생성으로 완벽 해결.
- **판단 기준**: 교육 현장에서 rate 없는 무한루프 사고가 실제로 잦으면 착수, 아니면 보류.

## 7.4 트레이스백 개선 (Phase 1.4의 완성)

- numpy 등 패키지 내부 프레임도 필터링 대상에 추가.
- `input()` 미지원 안내: 호출 시 "winput 위젯을 사용하세요" 에러 메시지 (Pyodide에서 input은 동작 안 함).

## 완료 정의

- [ ] 7.1, 7.2, 7.4 구현 + examples/numpy_wave.py
- [ ] 7.3은 설계 판단 기록만 (ARCHITECTURE.md에 결정 추가)
- [ ] ROADMAP 갱신
