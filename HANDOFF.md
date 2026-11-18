# HANDOFF — 작업 이력과 다음 할 일

> 새 세션은 이 파일부터 읽는다. 세션을 끝낼 때 '이력'에 한 줄, '다음 할 일'을 갱신한다.

## 지금 상태 (2026-11-18)

- 방향성 확정: **1 Energy(₩120)를 낼 만한 '왜'를 설명하는 해설** · 답변 구조 ①결론 Ⓗ역대맥락 ②사실 ③RORR분석 ④근거·다음
- 기준 코드: L2 후처리 · L3 경기 종료 배치/서사 카드/묶음 · L4 표기 사전/가드레일/봉투 · Energy 규칙 — **테스트 26개 통과**
- **미확인**: 실서비스 레포(`piecomp/l3-R-D`, `piecomp/rorr-ask-renderer`) 코드와 아직 대조하지 않았다.
  이 레포는 Notion 태스크 문서의 계약·경로를 기준으로 썼다. 대조 후 각 층 문서의 '이식 위치' 표를 고쳐야 한다.

## 이력

| 날짜 | 누가 | 내용 |
|---|---|---|
| 2026-11-14 | Jun + Claude | Notion·태스크 DB·온톨로지 현황 파악 → 방향성(4층 답변, Energy 원칙, 단계 P0~P2) 작성 · HTML 목업(대표 질문 3개) |
| 2026-11-14 | Jun + Claude | 역대 서사 레이어 추가 — 2026 데이터만으론 "T1은 BLG에 약하다"로 읽힘, 서사 카드로 보충 후 P3에 역대 데이터 적재 |
| 2026-11-18 | Jun + Claude | rorr-layer-core 생성 — 층별 문서 · 계약 스키마 · 기준 코드 · 테스트 · DDL · 이 인계 파일 |
| 2026-11-18 | Jun + Claude | 작업을 Claude Code CLI(~/Documents/rorr-layer-core)로 이관 — push · 기존 코드 대조는 CLI에서 |

## CLI 인계 (2026-11-18 — Cowork 세션 → Claude Code CLI)

작업 폴더: `~/Documents/rorr-layer-core` (이 레포). Cowork 세션에서는 GitHub 접근이 막혀 push 와 기존 코드 대조를 못 했다.
CLI 에서 처음 할 일:

1. **push** — `git push -u origin main` (origin = github.com/zzunlsj/rorr-layer-core 설정됨).
   원격에 README 같은 첫 커밋이 이미 있으면 `git pull --rebase origin main` 후 push.
2. **기존 코드 대조** — `rorr-repos/` 에 `piecomp/l3-R-D`, `piecomp/rorr-ask-renderer` 를 클론하고
   `CLAUDE.md §5` 의 '확인된 위치' 와 `docs/01·02·03` 의 '이식 위치' 표를 실제 경로로 고친다.
   (`rorr-repos/` 는 `.gitignore` 에 있어 이 레포에 커밋되지 않는다)
3. 대조하면서 계약(contracts/)이 실제 응답과 다른 곳은 `docs/decisions.md` 에 남기고 schema · contracts.py 를 같이 고친다.

CLI 첫 프롬프트 예시:
> HANDOFF.md 와 CLAUDE.md 를 읽고, rorr-repos/ 의 l3-R-D · rorr-ask-renderer 코드와 docs/01~03 의 '이식 위치' 표를 대조해서 실제 파일 경로로 고쳐줘. 계약이 실제 응답과 다르면 decisions.md 에 기록해줘.

## 다음 할 일

### 바로 (P0 — Worlds 결승 직후)
1. [L2·L3 담당] `l3-R-D` 코드와 대조 → `docs/01`, `docs/02` 의 '이식 위치' 표 확정
2. [L4 담당] `rorr-ask-renderer` 에 `l4/glossary.py` + `l4/guardrails.py` 이식 → faker 로그 4개 문제(G1·G2·G3·G5) 재발 방지
3. [Jun] 서사 카드 첫 묶음 등록 — nf-0001(T1 Worlds LPL 상대 기록)의 **기준(녹아웃/전체, 시작 연도) 확정**이 먼저
4. [L3 담당] `sql/001_match_report_lens.sql` 적용 + Worlds 4강·결승 경기로 배치 1회 실행

### 다음 (P1 — 11/15 이후)
5. LwRC+ 팀·선수 ID 매핑 → `lwrc_by_game` · `lwrc_cdr` lens 연결
6. 정답셋에 '왜' 질문(해석 카테고리) 추가 — 현재 183건 중 0건
7. D-008 결정 (L4 1회 vs 2회 호출)

전체 태스크 초안: `docs/tasks.md` (Notion 태스크 DB 등록 전 검토용)

## 열린 질문 (docs/decisions.md '미결')

- 사실형 질문(일정·로스터·용어)도 1 Energy인가
- 유료 답변에 RORR 분석 필수인가 (G10 은 지금 warn)
- scope 우선순위 맥락 > 텍스트 > DB 확정 여부
- 서사 카드 관리 주체 · 역대 데이터 소스와 라이선스
