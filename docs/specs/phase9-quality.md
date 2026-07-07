# Phase 9 스펙 — 호환성 검증 & 품질 (상시)

## 9.1 GlowScript 호환성 스위트

glowscript.org 대표 예제를 `compat/` 폴더에 수집 (원본 출처 주석 필수):
Bounce, Binary star, Color-RGB-HSV, Rug, Stonehenge, Plot3D, Wave,
그리고 Matter & Interactions 교과서 예제 몇 개 (물리 교육 실사용 검증).

각 파일 상단에 요구 phase 주석: `# requires: phase2(helix), phase4(scene.range)`
→ 해당 phase 완료 시 이 파일을 실행해 보는 것이 완료 조건의 일부.

## 9.2 자동 회귀 테스트

수동 육안 확인의 한계를 넘기 위한 헤드리스 테스트:
- Node + Playwright로 페이지 로드 → 예제 코드 주입 → N초 실행 → 판정:
  ① 콘솔 에러 0건 ② `vpw.objects.size`가 기대값 ③ 지정 객체의 pos가 움직였는지.
- `tests/e2e/run_examples.spec.js` — examples/ + compat/ 전체 순회.
- GitHub Actions에서 push마다 실행 (`microsoft/playwright-github-action`).
- 이것이 도입되면 CLAUDE.md의 검증 체크리스트를 "npm test 통과"로 교체.

## 9.3 단위 테스트

- Phase 3에서 도입한 `tests/test_vector.py` (pytest, 로컬 CPython) 유지·확장.
- 변환기(rate→await) 테스트: 문자열/주석/이미 await/메서드 호출 케이스.

## 9.4 성능 벤치마크

- `compat/bench_1000.py`: 구 1,000개 + rate(100). 판정: requestAnimationFrame 간격 평균 < 20ms.
- 측정 코드를 renderer.js에 내장 (`vpw.stats()` → {fps, objectCount}) — 테스트에서 조회.
- 미달 시 최적화 순서: ① 배칭 확인 ② geometry 공유 ③ InstancedMesh (동일 type 대량) ④ 그때도 안 되면 Worker.

## 9.5 모바일/접근성

- 터치: OrbitControls는 기본 지원. 에디터/버튼 레이아웃만 반응형 (좌우 → 상하 전환 @768px).
- iOS Safari에서 Pyodide 동작 확인 (메모리 제약 이슈 가능성).

## 9.6 문서화

- `docs/API.md`: 구현된 API 레퍼런스 (phase 완료 때마다 갱신).
- `docs/DIFFERENCES.md`: GlowScript와 다른 점 (진짜 CPython, numpy 가능, 미구현 목록).
- README에 라이브 데모 링크 + 스크린샷/GIF.

## 완료 정의

상시 트랙이므로 "완료"가 아니라 각 phase의 완료 조건에 9.1/9.2 통과를 포함시키는 방식으로 운영.
