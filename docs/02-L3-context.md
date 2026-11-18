# 02. L3 — 컨텍스트 조립 층

담당 레포: `piecomp/rorr-backend-ai` (`src/chat/` · `src/rag/` — 옛 표기 `rorr-ai-server`, D-020) · 프롬프트·측정: `piecomp/l3-R-D` · 기준 코드: `src/rorr_layer_core/l3/` · DDL: `sql/`

## 지금 (`rorr-backend-ai` `dev` `0fa7b22` 코드 확인, 2026-11-18)

- **운영 · 개발 모두 `md` 모드**: `L3_PROMPT_MODE=md` · `L3_QUERY_MODEL=claude-sonnet-4-6` · `L3_GEN_MODE=agent` (`deploy-prod.yml` · `deploy-dev.yml`). 프롬프트는 `src/chat/l3/prompts/*.md` 7개.
- 흐름: 정규식 보정(metrics · role · intent · scope) → 진행 중 경기 확인 → RAG 캐시(`prepared_questions`, 진행 중 경기면 건너뜀) → agent 쿼리 생성(조회해 보며 고친 뒤 `submit_query` **1개**, 10턴 · 25초 한도) → 1행 이상이면 RAG 저장 → `callCascade` → 웹 L4 `/render`. 요청 전체 한도 42초.
- 정적 템플릿 45개는 꺼져 있다 (2026-11-04). legacy 경로(Haiku 생성 · scope 폴백 · T1-bot)는 코드에 남아 있지만 `md` 모드에서는 타지 않는다.
- L4 로 넘기는 데이터는 `retrieval.qa = [{q, a: rows, source}]` **하나**다.
- 측정 (`l3-R-D` `stage2_full`, Sonnet 5.5 단발 생성 기준): 개발용 70문항 95.7% · 94.3%, 문항당 약 $0.045, 중앙값 약 5.5초 — **운영 구성(Sonnet 4.6 agent)과 다르므로 원가 · 지연은 다시 재야 한다.**
- 원가 (Notion 실측, 위와 같은 전제): 질문 1건 평균 ₩41 (L3가 전체의 98%), 캐시 히트 ₩0, 상위 10% ₩177+ (판매가 초과)
- 테스트 183건 중 해석 카테고리(match_review · player_review · turning_point · teamfight_analysis) **0건**

## v2 변경 — 기존 쿼리 생성은 그대로 두고 뒤에 붙인다

### 1) 경기 종료 배치 — `l3/match_report.py` · `sql/001_match_report_lens.sql`
경기가 끝나면 팀별로 1행씩 미리 계산 → 질문 시점엔 `(game_id, subject_side)` 로 읽기만 (Sonnet 0회).

| lens | 입력 (query 조회 가이드) | 계산 |
|---|---|---|
| winprob_curve | `win_probability_frame` (= 한타 승률, 이름 변경 예정) | 5~95% 클램프 · 변곡점(60초 안 20%p 이상) |
| objective_swing | `v_objective_swing` + `obj_intensity_weight` | swing_gold_60s × intensity, **주어 팀 기준 부호** · Top3 |
| death_breakdown | `v_kill_damage_breakdown` | 변곡점 ±30초 안 주어 팀 첫 데스 · 가해자별 비중 · 솔로성(80%↑) |

트리거: 경기 종료(`match.state = completed`) 이벤트 → 배치 1회. 실패 시 질문 시점에 동일 함수로 즉석 계산(폴백).

### 2) lens 레지스트리 — `l3/lenses.py`
- intent → lens 목록은 L2 `INTENTS` 에서 (단일 소스).
- `precomputed` lens 는 배치에서 읽고, 아닌 것(gold_diff_by_minute · first_objective_rate · role_matchup)은 쿼리 생성 → **첫 생성 후 prepared_questions 캐시에 올린다**.
- 경기가 특정되지 않으면 경기 단위 lens 는 붙이지 않는다.
- LwRC+ lens(`lwrc_by_game`, `lwrc_cdr`)는 LwRC+ 팀·선수 ID 매핑(11/15 이후) 완료가 전제.

### 3) 서사 카드 — `l3/narrative.py` · `sql/002_narrative_fact.sql`
- `status = verified` · 유효 기간 안 · 질문 엔티티(+상대 팀 리그 코드) 매칭 카드만, 기본 1장.
- 상대가 지정된 카드(entity_b)는 질문 상대와 맞을 때만. 두 엔티티가 모두 맞는 카드 우선.
- P3(역대 데이터 적재) 후 `auto_derived = true` 카드가 같은 테이블로 들어온다 — L3/L4 코드는 그대로.

### 4) L3Bundle — `l3/bundle.py`
L4로 넘기는 묶음에 다음을 추가: `lenses · narratives · teams(side→팀 코드) · data_scope("2026") · sources · cost_krw · outcome`.
`outcome` 은 Energy 판단의 유일한 입력이다 — `answered · no_data · l3_failed · off_domain · clarify · system_error`.

## 이식 위치 (2026-11-18 대조 — 코드 확인)

`piecomp/l3-R-D` 는 측정 하니스라 여기에 이식하지 않는다. 실서비스 L3 는 `piecomp/rorr-backend-ai` 다. 현황 전체는 `docs/05-current-vs-target.md` §4.

| 기준 코드 | 이식 위치 | 상태 |
|---|---|---|
| `build_match_report` | 경기 종료 이벤트 컨슈머 (Kafka 트리거 있음 — 대화 레이어 구조 §6) | ❌ 받은 6개 레포에 없음 — 컨슈머 레포 미확인 |
| `plan_lenses` · `assemble` | `rorr-backend-ai` `src/chat/chat.service.ts` `generate()` — `l3Query.generateAndRun()` 뒤, `callCascade()` 앞 | ✅ 위치 확인 |
| L3Bundle 전달 | 같은 파일 `callCascade()` 의 `body` 조립부 (`retrieval.qa` 를 만드는 곳) + `chat.types.ts` | ✅ 위치 확인 · D-016 |
| `outcome` | `chat.types.ts GenerateResponse` + `generate()` 의 반환점들 (`_monPush`) | ✅ 위치 확인 |
| `NarrativeStore.match` | `rorr-backend-ai` `src/rag/rag.service.ts` 옆 Postgres 조회 함수 (sql/002 쿼리) | ✅ 위치 확인 |
| `INTENTS` → 테이블 매핑 | `src/chat/source-mapping.ts` — legacy · RAG 경로에서만 쓰인다. `md` 모드는 intent 를 힌트로만 넘긴다 (`buildL2Hint`) | ✅ 위치 확인 |
| lens 쿼리 프롬프트 | `rorr-backend-ai` `src/chat/l3/prompts/routing.md` · `examples.md` — 분석 뷰 용도 · 예시 쿼리가 이미 운영 프롬프트에 있다. 측정은 `l3-R-D` 에서 먼저 | ✅ 위치 확인 |
| '왜' 정답셋 | `l3-R-D` `goldset/dev.json` (형식: 질문 + 정답 SQL + `check`) | ✅ 위치 확인 |

### 대조에서 확인된 것

- **입력 테이블·뷰는 dev DB 에 있다** (`l3-R-D/context/schema.md`): `win_probability_frame(game_time, win_prob_100)` · `v_objective_swing(swing_gold_60s, category, side)` · `v_kill_damage_breakdown(source, caster_id, total, sequence_index)`. `game_time` 은 밀리초, `game_id` 는 텍스트다.
- **`obj_intensity_weight` 는 스키마 덤프에 없지만 운영 프롬프트는 쓴다.** `rorr-backend-ai` `prompts/examples.md` 가 "`category` → `intensity` 설정 테이블" 로 설명하고 예시 쿼리에서 JOIN 한다. DB 에 실제로 있는지만 확인하면 된다 (D-018).
- **`match.state` 값은 `unstarted` / `completed` / `cancelled`** 다 (`context/codes.md`). 배치 트리거 조건 `completed` 는 맞다. 다만 `live_game.state` 는 끝난 게임이 `in_progress` 로 남으므로 게임 단위 종료 판단에 쓰면 안 된다.
- **캐시 방침이 충돌한다 — 운영은 지금 저장한다.** `generate()` 는 생성 쿼리를 1행 이상이면 `prepared_questions` 에 저장한다 (주석: "다른 선수 · 팀 질문에 히트되면 틀릴 수 있음, 테스트용으로 감수"). 위 2) 는 "첫 생성 후 `prepared_questions` 캐시에 올린다" 인데, `l3_alignment.md` 는 새 방식에서 생성 쿼리를 RAG 에 **저장하지 않는 것**을 1차 추천한다 (값을 쿼리에 직접 써서 "T1 몇 위야?" 쿼리가 "젠지 몇 위야?" 에 재사용되는 문제). lens 쿼리 캐시는 이 결정을 따라야 한다 (D-019).
- **wGE = LwRC.** DB 컬럼은 `wge_player_game.wge_plus` 등 옛 이름이고, L4 가 화면에서 `LwRC+` 로 바꾼다 (`formatter._lwrc`). lwrc lens 는 이 테이블을 읽는다.
- **정답셋에 해석 문항이 없다는 것도 확인.** `goldset/dev.json` 70문항의 L2 intent 는 `game_state` 18 · 일정/순위 거절 34 등이고 `match_review` 류는 0건이다.

## 수용 기준

- [ ] 목업 Q1 데이터로 변곡점 24:00 · 스윙 Top3 · 데스 분해 46/36/18 (`tests/test_l3.py`)
- [ ] Worlds 4강·결승 경기 배치 실행 → match_report_lens 행 생성
- [ ] 배치 lens 만 쓰는 질문은 query_cost 로그의 sonnetCalls = 0
- [ ] 정답셋에 해석 카테고리 '왜' 질문 20건 이상 추가
- [ ] 0행 결과는 캐시에 저장하지 않는다 (현재 L3 진단의 문제 — 별건이지만 같이 확인)
