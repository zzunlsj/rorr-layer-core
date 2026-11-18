# 결정 로그

상태: **확정**(Jun 승인) · **제안**(이 레포 기준안, 담당 논의 필요) · **미결** · **확인**(레포 대조로 확인한 사실)

| ID | 날짜 | 상태 | 결정 | 근거 / 비고 |
|---|---|---|---|---|
| D-001 | 2026-11-14 | 확정 | 답변 구조: ①결론 Ⓗ역대맥락 ②사실 ③RORR 분석 ④근거·서하·다음 | Notion 방향성 §2, 목업 |
| D-002 | 2026-11-18 | 제안 | intent 레지스트리를 한 파일(`l2/intents.py`)로 단일화, 버전 표기. team_compare 추가, matchup_pattern 신규 | L2 35종 vs L3 34종 불일치 (L3 프로세스) |
| D-003 | 2026-11-18 | 제안 | question_form · subject · intent 승격은 규칙 기반 후처리 (Jev 호출 추가 없음) | 라우터에 LLM 판정 금지 원칙 · Jev 비용 |
| D-004 | 2026-11-18 | 제안 | 계약 변경 시 schema.json · contracts.py · 층 문서 동시 수정 | — |
| D-005 | 2026-10-23 | 제안 | scope 우선순위 맥락 > 텍스트 > DB | 대화 레이어 구조 §9-1, 기존 두 태스크 기록이 반대 |
| D-006 | 2026-11-14 | 확정 | 해설형 RORR 분석은 경기 종료 배치로 미리 계산 (match_report_lens) | 방향성 §3 경제성, L3 원가 p90 > 판매가 |
| D-007 | 2026-11-14 | 확정 | 역대 서사는 지금 서사 카드(검증)로 보충, 나중에 역대 데이터 적재 후 자동 도출 | Jun 요청, 방향성 4-1 |
| D-008 | — | 미결 | L4 호출 1회(emit_viz 확장) vs 2회(emit_viz + emit_answer) | 캐시 prefix 크기·지연 측정 후 |
| D-009 | — | 미결 | Energy: 사실형 질문 과금 여부 · 유료 답변 RORR 분석 필수 여부(G10 block 승격) | 방향성 §6 결정 필요 1~3 |
| D-010 | — | 미결 | 서사 카드 관리 주체·검증 절차, nf-0001 기준(녹아웃/전체, 시작 연도) | 방향성 §6 결정 필요 6~7 |
| D-011 | — | 미결 | 역대 데이터 소스·라이선스·적재 범위 | 방향성 4-1 |
| D-012 | — | 미결 | win_probability_frame → 한타 승률 테이블 이름 변경 시점 | LoL 데이터 레이어 메모 |
| D-013 | 2026-11-18 | 확인 | `piecomp/l3-R-D` 는 L2 라우터도 L3 서비스도 아니다 — L3 쿼리 생성 **측정 하니스**(TS). L3 실서비스 = `rorr-ai-server` (`src/chat/` · `src/rag/`), L2 Jev 레포는 미확인 | `l3-R-D` `main` `a1eaf87` 에 `jev.py` · `judge_route` · `source-mapping.ts` · `scope.service.ts` · 브랜치 `feat/jev-judge` 없음. `rorr-ai-server` 는 접근 권한 없음. 정답셋 `l2` 필드는 옛 형식 `{intent, scope, entity, entity_type, metric, layer}` · 옛 intent 이름(`victory_analysis` 등) |
| D-014 | 2026-11-18 | 확인 | 현행 L4 계약: 요청 = AI 서버 `GenRequest` (`intent.type` · `retrieval.qa[0].{q,a,source}` · `meta.lang`), 응답 = `{title, text, viz}`. kind = `card` · `ranking` · `compare` + 코드 폴백 `table` · `text` | `rorr-ask-renderer` `dev` `9e8ebe7` `app.py` · `prompts.py` · `contract.md`. Notion 기준(37 kind · temperature 0 · few-shot 상주)과 다르다 — docs/03 '실제 코드' |
| D-015 | — | 미결 | AnswerEnvelope ask-v2.0 과 현행 봉투의 관계. `facts{kind, rows, meta}` 는 현행 `viz` 모양(`stats[]` · `rows[]{label,value}` · `columns/entities` · `columns/rows[][]`)과 맞지 않는다. **제안:** `facts` 에 현행 `viz` 봉투를 그대로 넣고, v2 봉투는 응답에 `version` 으로 구분되는 새 필드로 추가 (기존 웹 렌더 깨지지 않게). `lead.text` 와 `viz.text`(상세 답변) 중복 처리도 같이 정한다 | schema · `contracts.py` 는 결정 전이라 고치지 않았다 |
| D-016 | — | 미결 | L3Bundle 전달 경로. 현행 `GenRequest` 에는 `lenses` · `narratives` · `teams` · `outcome` · `route`(주어·극성) 자리가 없고 `to_l3()` 는 `qa[0]` 하나만 읽는다. **제안:** `retrieval` 아래에 `lenses` · `narratives` 를, 최상위에 `route` · `outcome` 을 추가 (없으면 현행 동작) | `rorr-ai-server` `callCascade` 쪽 코드를 봐야 확정 가능 — 접근 권한 필요 |
| D-017 | — | 미결 | 현행 L4 규칙과 충돌 3건: (a) G6 표 10행 접기 ↔ 현행 "전 행, 자르지 않음" (b) G3 진영 → 팀 코드 ↔ 현행 블루/레드 (c) "LLM 초안 숫자는 쓰지 않는다" ↔ 현행 `text` 는 숫자 인용 상세 답변 | L4 담당과 합의. (a) 는 최근 PR `fix/large-table-rendering` 이 의도적으로 정한 동작 |
| D-018 | — | 미결 | `obj_intensity_weight` 테이블이 dev DB 스키마 덤프에 없다 — objective_swing 의 intensity 가중치 출처 | `l3-R-D/context/schema.md`. `sql/001` 주석의 JOIN 이 실행되지 않을 수 있다 |
| D-019 | — | 미결 | lens 쿼리를 `prepared_questions` 에 캐시할지. L3 이관안은 새 방식에서 생성 쿼리를 RAG 에 저장하지 않는 것을 1차 추천 (엔티티·날짜가 쿼리에 박혀 재사용 시 오답) | `l3-R-D/etc/l3_alignment.md` 'RAG 재사용과 충돌'. docs/02 2) 의 "두 번째부터 ₩0" 전제가 여기에 달려 있다 |
| D-020 | 2026-11-18 | 확인 | D-013 의 미확인 레포를 찾았다 — L2 Jev = `piecomp/rorr-user-intent-router` (`src/embedder/jev.py` `judge_route`), 소켓 scope = `piecomp/rorr-socket-server` `dev` (`src/gateways/scope.service.ts`), L3 실서비스 = `piecomp/rorr-backend-ai` (문서의 `rorr-ai-server`) | Notion '대화레이어시스템 github 정리' 의 6개 레포를 `rorr-repos/` 에 클론. 파일·함수 위치만 확인, 동작 대조는 아직 (CLAUDE.md §5). D-016 의 `callCascade` 도 이제 볼 수 있다 |
| D-021 | 2026-11-18 | 확인 | 운영 L3 는 이미 `md` 모드다 — Sonnet 4.6 · agent 방식(조회해 보며 고친 뒤 쿼리 1개 제출) · 생성 쿼리는 1행 이상이면 RAG 저장 · 정적 템플릿 꺼짐. L4 로는 `retrieval.qa[0]` 하나만 간다 | `rorr-backend-ai` `dev` `0fa7b22` `deploy-prod.yml` · `chat.service.ts` · `l3-query.service.ts`. docs/02 '지금' 을 고쳤다. 원가 · 지연 측정값(Sonnet 5.5 단발 기준)은 다시 재야 한다 |
| D-022 | 2026-11-18 | 확인 | L2 필드 전달 현황 — 소켓은 `verdict · path · unresolved` 를 넘기고 `null_reason` 만 안 읽는다. 백엔드가 AI 서버로 넘길 때 `verdict · path · unresolved` 를 버린다. scope 는 라우터 · 소켓 · AI 서버 세 곳에서 정한다 | `rorr-socket-server` `affect-api.service.ts` · `rorr-backend-api-v2` `affect.controller.ts` · `rorr-user-intent-router` `scope.py`. docs/01 '문제 4 · 5' 를 고쳤다 |
| D-023 | — | 미결 | Energy 반환 조건을 `outcome` 기준으로 바꿀지. 현행은 선차감 후 `text` 가 비었거나 `l4-web-fallback` 일 때만 반환 — 코드상 데이터 없음 · 롤 밖 질문은 차감된다. **제안:** AI 서버 응답에 `outcome` 추가, 백엔드는 `outcome !== 'answered'` 면 반환 (선차감은 유지) | docs/05 §6. 운영 로그로 실제 차감 여부부터 확인. D-009 와 같이 결정 |
