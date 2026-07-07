# Phase 8 스펙 — IDE/플랫폼 기능

> 서비스화 단계. 8.1~8.5는 서버 없이 가능, 8.6(클라우드 저장)만 Supabase 필요.

## 8.1 예제 갤러리

- `examples/index.json` 작성: `[{ "file": "bouncing_ball.py", "title": "튀는 공", "desc": "..." }]`
- 헤더에 드롭다운 → 선택 시 fetch해서 에디터에 로드 (수정 중이면 확인창).
- 새 예제 추가 시 index.json 갱신을 CLAUDE.md 워크플로에 추가.

## 8.2 로컬 저장

- 자동 저장: 에디터 변경 2초 디바운스 → localStorage (`vpw:autosave`). 접속 시 복원 제안.
- 파일 열기/저장: File System Access API (`showSaveFilePicker`) + 미지원 브라우저는 다운로드 폴백.

## 8.3 공유 (서버 없이)

- **URL 공유**: 코드를 lz-string(CDN)으로 압축 → `#code=...` 해시. 접속 시 해시 있으면 디코드.
  URL 2,000자 제한 안내 (초과 시 경고).
- **단일 HTML 내보내기**: 현재 코드 + vpython.py + renderer.js를 인라인으로 묶은
  자립형 HTML 생성 (CDN 의존은 유지). 템플릿 문자열 방식으로 main.js에 구현.
  GlowScript의 export 대응 기능 — 학생 과제 제출용.

## 8.4 GitHub Pages 자동 배포

`.github/workflows/pages.yml`:
```yaml
on: { push: { branches: [main] } }
permissions: { contents: read, pages: write, id-token: write }
jobs:
  deploy:
    environment: { name: github-pages, url: ${{ steps.deployment.outputs.page_url }} }
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/upload-pages-artifact@v3
        with: { path: '.' }
      - id: deployment
        uses: actions/deploy-pages@v4
```
리포 Settings → Pages → Source를 "GitHub Actions"로 변경 필요 (수동 1회).

## 8.5 에디터 개선 (선택)

- Monaco 전환 여부: CodeMirror 5로 충분하면 유지. 전환 시 자동완성(vpython API 목록) 같이.
- 최소한 CodeMirror에 Ctrl+Enter=Run 단축키, 자동 들여쓰기는 추가.

## 8.6 클라우드 저장 (Supabase)

### 스키마

```sql
create table profiles ( id uuid primary key references auth.users, username text unique );
create table folders (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null references auth.users,
  name text not null
);
create table programs (
  id uuid primary key default gen_random_uuid(),
  owner uuid not null references auth.users,
  folder_id uuid references folders,
  title text not null default 'untitled',
  code text not null default '',
  is_public boolean not null default false,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);
```

### RLS 정책 (핵심 — anon 키가 공개되므로 이것이 보안의 전부)

- programs: `select` — `owner = auth.uid() or is_public`; `insert/update/delete` — `owner = auth.uid()`.
- folders: 전부 `owner = auth.uid()`.
- **service_role 키는 클라이언트에 절대 포함 금지** (CLAUDE.md에도 명시됨).

### 클라이언트

- supabase-js v2 CDN. 로그인: 구글 OAuth (교육 대상 고려. 리디렉트 URL에 GitHub Pages 도메인 등록).
- UI: 헤더에 로그인 버튼 + "내 프로그램" 사이드 패널 (목록/저장/다른 이름으로/삭제/공개 토글).
- 공유 링크: `?p=<uuid>` → is_public이면 익명도 조회 가능.
- 설정 분리: `src/config.js`에 SUPABASE_URL/ANON_KEY (이 파일은 커밋 — anon 키는 공개 가능).
- 무료 티어 주의: 1주 무활동 시 프로젝트 일시정지 → README에 기록.

## 완료 정의

- [ ] 8.1~8.4 (8.5 선택) → 이 시점에 "공개 가능한 서비스"
- [ ] 8.6은 Supabase 프로젝트 생성(수동) 후 착수. RLS 정책을 실제로 테스트
      (다른 계정으로 비공개 글 접근 시도가 거부되는지)
- [ ] ROADMAP 갱신
