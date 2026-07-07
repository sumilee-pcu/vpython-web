# Phase 6 스펙 — 그래프 & UI 위젯

> 물리 수업 활용의 핵심 (에너지 그래프, 파라미터 슬라이더).
> 문서: https://www.glowscript.org/docs/VPythonDocs/graph.html, controls.html

## 6.1 그래프 구현 방식 결정

방침: **의존성 추가 없이 canvas 2D로 자체 구현** (축, 눈금, 자동 스케일, 범례).
이유: Plotly는 4MB+로 과하고, 그래프 요구사항이 "실시간 점 추가"로 단순함.
자체 구현이 1~2일 이상 걸리면 uPlot(~50KB, CDN)으로 전환 허용 — 결정을 ARCHITECTURE.md에 기록할 것.

## 6.2 graph API

```python
g = graph(title='에너지', xtitle='t', ytitle='E', width=640, height=400,
          xmin=, xmax=, ymin=, ymax=,      # 미지정 시 자동 스케일
          scroll=True, xmax=10,             # 스크롤 그래프
          fast=True, align='left')
```
- DOM 위치: scene.caption 영역 아래 (Phase 4에서 잡은 컨테이너 구조 사용).
- 자동 스케일: 데이터 범위 + 5% 마진, 매 flush마다 재계산.

## 6.3 플롯 계열

```python
gc = gcurve(graph=g, color=color.red, label='KE', width=2)
gc.plot(x, y)                 # 단일점
gc.plot([(x1,y1), (x2,y2)])   # 다중점
gc.plot(pos=(x, y))           # 구형 시그니처도 허용
gc.delete()                   # 데이터 초기화
```
- `gdots` (산점도, radius), `gvbars` (세로 막대, delta=폭), `ghbars` (가로 막대).
- graph 미지정 시 마지막 생성된 graph에 붙음 (없으면 자동 생성 — VPython 동작).
- 성능: plot 호출은 데이터만 쌓고, 다시 그리기는 rate flush당 1회.

## 6.4 UI 위젯

전부 `scene.caption`/`scene.title` 영역(또는 graph처럼 별도 영역)에 HTML로 생성.
바인드 콜백은 Phase 5의 이벤트 큐 메커니즘 재사용 (proxy 직접 전달 금지).

| 위젯 | 시그니처 (기본값 문서 확인) | HTML |
|---|---|---|
| `button(text=, bind=f)` | f(b) 호출, `b.text` 변경 가능 | `<button>` |
| `slider(min=, max=, value=, step=, bind=f, length=)` | f(s), `s.value` | `<input type=range>` |
| `menu(choices=[...], selected=, bind=f)` | `m.selected` | `<select>` |
| `checkbox(text=, checked=, bind=f)` | `c.checked` | `<input type=checkbox>` |
| `radio(text=, checked=, bind=f, name=)` | 그룹은 name으로 | `<input type=radio>` |
| `wtext(text=)` | 동적 텍스트, `w.text` 대입으로 갱신 | `<span>` |
| `winput(bind=f, type='numeric', width=)` | Enter 시 f, `w.number`/`w.text` | `<input>` |

- 세대 교체 시 위젯 DOM 전부 제거 (`_new_run` → 렌더러 reset과 함께).
- 위젯 속성 대입(예: `b.text = "Stop"`)도 브리지로 반영 — `vpw.widgetOp(id, opJson)`.

## 완료 정의

- [ ] graph/gcurve/gdots/gvbars/ghbars + 위젯 7종
- [ ] examples/energy_graph.py (튀는 공 + KE/PE 실시간 그래프), examples/slider_gravity.py
- [ ] 그래프에 점 10,000개까지 프레임 유지 확인
- [ ] 기존 예제 회귀 통과, ROADMAP 갱신
