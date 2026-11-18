# HANDOFF — 작업 이력과 다음 할 일

> 새 세션은 이 파일부터 읽는다. 세션을 끝낼 때 '이력'에 한 줄, '다음 할 일'을 갱신한다.

## 지금 상태 (2026-11-18)

- 방향성 확정: **1 Energy(₩120)를 낼 만한 '왜'를 설명하는 해설** · 답변 구조 ①결론 Ⓗ역대맥락 ②사실 ③RORR분석 ④근거·다음
- 기준 코드: L2 후처리 · L3 경기 종료 배치/서사 카드/묶음 · L4 표기 사전/가드레일/봉투 · Energy 규칙 — **테스트 26개 통과**
- **레포 대조 (2026-11-18)**: `piecomp/l3-R-D` · `piecomp/rorr-ask-renderer` 를 `rorr-repos/` 에 클론해 대조했다. 결과는 `CLAUDE.md §5` · `docs/01~03` '이식 위치' · `docs/decisions.md` D-013~D-019.
  - **L4 는 확정** — `rorr-ask-renderer` 의 `formatter.py` · `prompts.py` · `app.py`. 다만 현행은 kind 3종 · 응답 `{title, text, viz}` 로 Notion 기준과 다르다 (D-014).
  - **L3 · L2 레포를 찾아 동작까지 대조했다 (D-020~D-023)** — Notion '대화레이어시스템 github 정리' 의 6개 레포를 `rorr-repos/` 에 클론. 결과는 **`docs/05-current-vs-target.md`** (층별 지금 동작 · 목업까지 바꿀 것 · 순서).
  - **가장 큰 간극은 L3 → L4 전달 구조다.** 지금은 쿼리 1개 → `retrieval.qa[0]` 1묶음 → 카드 1장. 목업의 분석 3종 · 역대 맥락 · 주어를 실을 자리가 없다.
  - **운영 L3 는 이미 `md` 모드** (Sonnet 4.6 agent). 원가 · 지연 측정값은 다시 재야 한다 (D-021).
  - **Energy**: 코드상 데이터 없음 · 롤 밖 질문도 차감되는 것으로 읽힌다 — 운영 로그 확인 필요 (D-023).
- **채널 전체 방향 (2026-11-18)**: Muse 쪽 Notion 문서(레이어 허브 · 3채널 원칙 · 발화 · 친밀도 · Fan심 · Web/Extension 초안)와 대조했다 → **`docs/06-channels-and-muse.md`** · D-024~D-031.
  - 층 구조는 유지. **봉투는 플랫폼별로 묶는다 (Jun 방향, 비용 고민 중)** — 웹 = Energy 받는 리포트 봉투(ask-v2.0, `muse` 없음), 확장 = 비용 0 의 Muse 메시지. 웹의 서하 한 줄은 확장이 같이 켜졌을 때 SD 서하가 덧붙이는 별도 메시지 (D-025 · D-026). **L3 깊이도 채널별** — 확장은 쿼리 1개 · 낮춘 모델, 웹은 사실 + lens 3종 이상 (D-034). 남은 비용 질문은 D-033.
  - **기준은 기능 명세서, 현행 코드는 임시 (D-032, Jun 확정).** 그래서 서하 수치 금지(D-027) · 친밀도 명세 모델(D-028)은 명세 쪽으로 방향 확정. 과도기 처리와 세부 수치만 남았다.
  - **맥락 기억은 세 영역 다섯 칸** — 전체 공통 / Muse↔유저 단기 · 장기 / Ask RORR↔유저 단기 · 장기 (D-031). Notion 'Muse - 대화 History' 에 초안을 올렸다. 이 레포에 걸리는 곳은 L2 슬롯 기본값(이어 묻기)과 턴 레코드(`gist` · `card_ref`) 둘이다.
  - `game_end` 를 받는 Kafka 컨슈머를 `rorr-backend-api-v2` 에서 찾았다 — 배치 자리 후보 (D-029).
- **계약은 고치지 않았다.** v2 봉투 · L3Bundle 을 현행 `GenRequest` / `viz` 에 어떻게 얹을지가 미결이다 (D-015 · D-016).
- **로컬 환경**: 시스템 Python 은 3.9.6 뿐이라 `.venv` (3.9 + pytest)로 테스트를 돌린다 — `.venv/bin/python -m pytest -q`. `pyproject.toml` 은 3.11 이상을 요구하지만 지금 코드는 3.9 에서 26개 모두 통과한다.

## 이력

| 날짜 | 누가 | 내용 |
|---|---|---|
| 2026-11-14 | Jun + Claude | Notion·태스크 DB·온톨로지 현황 파악 → 방향성(4층 답변, Energy 원칙, 단계 P0~P2) 작성 · HTML 목업(대표 질문 3개) |
| 2026-11-14 | Jun + Claude | 역대 서사 레이어 추가 — 2026 데이터만으론 "T1은 BLG에 약하다"로 읽힘, 서사 카드로 보충 후 P3에 역대 데이터 적재 |
| 2026-11-18 | Jun + Claude | rorr-layer-core 생성 — 층별 문서 · 계약 스키마 · 기준 코드 · 테스트 · DDL · 이 인계 파일 |
| 2026-11-18 | Jun + Claude | 작업을 Claude Code CLI(~/Documents/rorr-layer-core)로 이관 — push · 기존 코드 대조는 CLI에서 |
| 2026-11-18 | Jun + Claude | CLI: `origin/main` push · 두 레포 클론·대조 → CLAUDE.md §5 · docs/01~03 '이식 위치' · decisions D-013~D-019 · 레포 이름 표기 정정 |
| 2026-11-18 | Jun + Claude | CLI: Notion 레포 목록대로 5개 레포 추가 클론 (`rorr-backend-ai` · `rorr-user-intent-router` · `rorr-socket-server` · `rorr-backend-api-v2` · `rorr-ollama-server`) → CLAUDE.md §1·§5 위치 갱신 · D-020 |
| 2026-11-18 | Jun + Claude | CLI: 새 레포 동작 대조 → `docs/05-current-vs-target.md` 신규 · docs/01·02·04 '지금' · '이식 위치' 를 코드 기준으로 수정 · D-021~D-023 |
| 2026-11-18 | Jun + Claude | Notion 에 개발자 검토 자료 등록 — 방향성 페이지 맨 위 참고 콜아웃 + 하위 문서 5개 (허브 · L2 · L3 · L4 · Energy). 링크는 `docs/sources.md` |
| 2026-11-18 | Jun + Claude | CLI: 웹 · 확장 두 채널 기준으로 방향 재검토 — Muse Notion 문서 7개 + affect · game-event · ollama 코드 대조 → `docs/06-channels-and-muse.md` 신규 · D-024~D-031 · sources 링크 |
| 2026-11-18 | Jun + Claude | CLI: Jun 방향 반영 — 명세가 기준 · 코드는 임시(D-032) · 플랫폼별 봉투(D-025 · D-026) · L3 깊이 채널별(D-034) · 맥락 기억 세 영역(D-031). Notion 'Muse - 대화 History' 에 기억 구조 초안 작성 |

## CLI 인계 (2026-11-18 — Cowork 세션 → Claude Code CLI)

작업 폴더: `~/Documents/rorr-layer-core` (이 레포). Cowork 세션에서는 GitHub 접근이 막혀 push 와 기존 코드 대조를 못 했다.
CLI 에서 처음 할 일 (**1·2 완료, 3 은 기록만** — 2026-11-18):

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
0. [Jun] **운영 로그로 두 가지 확인** — ① 데이터 없음 · 롤 밖 질문에 Energy 가 실제로 차감되는지 (D-023) ② 운영 L3(Sonnet 4.6 agent) 질문당 원가 · 지연 (`query_cost` 로그, D-021)
0-1. [L4 담당 · 백엔드] **docs/05 §7 의 A 단계** — 계약 변경 없이 바로 가능: `text` 프로즈 가드레일(G2 · G3 · G5 · G7) · `outcome` 기준 Energy 반환
0-2. [Jun] **레포 두 가지 더** — 웹 프런트(v2 봉투 렌더) · 확장 프런트(카드 자리 · 서하 반응 영역). 경기 종료 컨슈머는 후보를 찾았다 (D-029) — 거기에 붙일지 L3 담당과 확인
0-3. [Jun] **D-025 · D-026 · D-033 먼저** — 플랫폼별 봉투 확정 · SD 서하 첨언을 누가 쓰는지 · 확장의 '비용 0' 범위(L3 쿼리 생성을 안 부르는지). D-015 · D-008 을 정하기 전에 정해야 봉투와 `emit_answer` 를 두 번 바꾸지 않는다 (docs/06 §10)
0-4. [L3 담당] **확장용 얕은 조회 측정** — `l3-R-D` 로 정답셋 사실형만 골라 Haiku 급 `single` 의 방향 정확도 · 건당 비용 · 지연을 잰다 (D-034). 운영 Sonnet 4.6 agent 원가(D-021)와 같이 재면 비교가 된다
1. [L4 담당과] D-017 충돌 3건 합의 (표 10행 접기 ↔ 전 행 · 진영 팀 코드 ↔ 블루/레드 · `text` 숫자) — 이식 전에 정해야 한다
2. [L4 담당] `rorr-ask-renderer` `formatter.py` 에 `l4/glossary.py` + `l4/guardrails.py` 이식 → faker 로그 4개 문제(G1·G2·G3·G5) 재발 방지. 표 셀 변환은 이미 있고 **`text` 프로즈가 틈**이다 (docs/03 '가드레일 ↔ 이미 있는 코드')
3. [Jun] 서사 카드 첫 묶음 등록 — nf-0001(T1 Worlds LPL 상대 기록)의 **기준(녹아웃/전체, 시작 연도) 확정**이 먼저
4. [L3 담당] `sql/001_match_report_lens.sql` 적용 + Worlds 4강·결승 경기로 배치 1회 실행 — 먼저 `obj_intensity_weight` 가 DB 에 있는지 확인 (D-018)

### 다음 (P1 — 11/15 이후)
5. LwRC+ 팀·선수 ID 매핑 → `lwrc_by_game` · `lwrc_cdr` lens 연결
6. 정답셋에 '왜' 질문(해석 카테고리) 추가 — 현재 183건 중 0건
7. D-008 결정 (L4 1회 vs 2회 호출)
8. D-015 · D-016 결정 (v2 봉투 · L3Bundle 을 현행 `/render` 요청·응답에 얹는 방법 — `callCascade` 조립부를 이제 볼 수 있다, docs/05 §4) → schema · `contracts.py` · docs 동시 수정
9. D-019 결정 (lens 쿼리 캐시 — L3 이관안의 'RAG 저장 안 함' 과 충돌)

전체 태스크 초안: `docs/tasks.md` (Notion 태스크 DB 등록 전 검토용)

## 열린 질문 (docs/decisions.md '미결')

- 사실형 질문(일정·로스터·용어)도 1 Energy인가
- 유료 답변에 RORR 분석 필수인가 (G10 은 지금 warn)
- scope 우선순위 맥락 > 텍스트 > DB 확정 여부
- 서사 카드 관리 주체 · 역대 데이터 소스와 라이선스
- 친밀도 모델 (명세 ↔ 코드, D-028) · 웹 질문을 감정 · 관계 신호로 넣을지 (D-030) · 대화 타임라인 위치 (D-031)
