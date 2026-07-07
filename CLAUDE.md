# CLAUDE.md — vpython-web 작업 가이드

이 문서는 새 AI 세션/새 작업자가 대화 맥락 없이 이 프로젝트를 이어받기 위한 온보딩 문서다.
**작업 시작 전에 이 파일 → [docs/ROADMAP.md](docs/ROADMAP.md) → 해당 단계의 [docs/specs/](docs/specs/) 순서로 읽을 것.**

## 프로젝트가 무엇인가

브라우저에서 **진짜 CPython(Pyodide/WASM)** 으로 VPython 물리 시뮬레이션을 실행하는 웹 환경.
GlowScript(glowscript.org)의 대체물이지만, Python→JS 트랜스파일 대신 실제 파이썬 인터프리터를 쓰므로
numpy 등 파이썬 생태계를 그대로 활용할 수 있는 것이 차별점. 소유자: sumilee-pcu (교육용 물리 시뮬레이션 목적).

## 아키텍처 (요약)

```
에디터(CodeMirror) → [rate() → await rate() 변환] → Pyodide(CPython)
   → src/vpython.py (VPython API 계층) → JS 브리지(globalThis.vpw) → src/renderer.js (three.js/WebGL)
```

상세: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — 브리지 프로토콜, 실행 모델, 계획된 설계 변경 전부 여기 있음.

## 파일 맵

| 파일 | 역할 |
|---|---|
| `index.html` | 레이아웃, CDN 로드(CodeMirror/Pyodide/three.js importmap) |
| `src/main.js` | 실행 파이프라인: Pyodide 초기화, rate 변환, Run/중단 처리 |
| `src/vpython.py` | **VPython API 계층 (핵심 작업 대상)** — vector, 3D 객체, color, rate |
| `src/renderer.js` | three.js 씬/카메라/조명, createObject/updateObject/reset |
| `examples/*.py` | 예제 (호환성 테스트 겸용) |
| `docs/ROADMAP.md` | **진행 상태의 단일 진실 원천** — 체크박스로 완료 표시 |
| `docs/specs/phaseN-*.md` | 단계별 상세 스펙 (시그니처, 기본값, 수용 기준) |

## 불변 규칙 (지키지 않으면 기존 코드가 깨짐)

1. **브리지는 JSON 문자열만 주고받는다.** Python↔JS 간 Pyodide proxy 객체를 넘기지 말 것
   (수명 관리 버그의 온상). `vector`는 `[x, y, z]` 배열로, 색은 0~1 범위 RGB로 인코딩.
2. **세대(generation) 카운터**: Run을 다시 누르면 `_new_run()`이 세대를 올리고, 이전 실행의
   루프는 다음 `rate()`에서 `_Stopped` 예외로 종료된다. 새로 추가하는 모든 비동기 자원
   (이벤트 핸들러, 타이머 등)도 세대 확인으로 정리해야 한다.
3. **rate 변환은 줄 수를 보존한다.** 에러 줄번호가 사용자 코드와 일치해야 하므로,
   코드 변환 시 줄을 추가/삭제하지 말 것.
4. **`_Object3D._known`에 있는 속성만 렌더러와 동기화**되고, 나머지(velocity 등)는 자유 속성.
   새 동기화 속성을 추가하면 renderer.js의 `_applyProps`에도 반드시 대응 추가.
5. **서버 없는 정적 사이트를 유지한다.** 빌드 도구 도입 금지(현재 방침), 모든 라이브러리는
   CDN 또는 리포 내 파일. GitHub Pages에 그대로 배포 가능해야 한다.
6. 렌더러의 `updateObject`는 **모르는 id를 조용히 무시**한다 (이전 세대 잔여 호출 대비). 유지할 것.

## 개발 워크플로

1. ROADMAP.md에서 다음 미완료 항목 확인 → 해당 phase spec 읽기.
2. spec의 "공식 문서 확인" 표시가 있으면 구현 전 glowscript.org/docs/VPythonDocs/ 에서 기본값 재확인.
3. 구현 → 검증(아래) → spec의 수용 기준 통과 확인 → ROADMAP 체크박스 갱신 → 커밋.

### 실행/검증 방법

```bash
cd vpython-web
python -m http.server 8000   # file:// 로는 동작 안 함 (fetch 사용)
# http://localhost:8000 접속, 첫 로딩은 Pyodide 다운로드로 수십 초
```

검증 체크리스트: ① Run 클릭 시 예제가 돌아간다 ② 콘솔 에러 0건 ③ Run 재클릭 시
이전 시뮬레이션이 멈추고 새로 시작한다 ④ 기존 examples/ 전부 여전히 동작한다.

### 커밋 규칙

- 영어 커밋 메시지, 첫 줄은 "동사원형 + 무엇을" (예: `Add cylinder and arrow objects`).
- 기능 단위로 커밋. spec/ROADMAP 갱신은 해당 기능 커밋에 포함.
- 원격: https://github.com/sumilee-pcu/vpython-web (main 브랜치 직접 푸시).

## 현재 상태를 아는 법

`docs/ROADMAP.md`의 체크박스가 유일한 진실 원천이다. 이 파일이나 대화 기억이 아니라
ROADMAP과 실제 코드를 기준으로 판단할 것.
