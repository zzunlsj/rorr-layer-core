# 02. L3 — 컨텍스트 조립 층

담당 레포: `piecomp/l3-R-D` · 기준 코드: `src/rorr_layer_core/l3/` · DDL: `sql/`

## 지금

- 흐름: 정규식 보정 → 캐시(Redis → e5 0.94) → 템플릿 → Sonnet 쿼리 생성 → 0행이면 scope 바꿔 재시도 → T2
- 측정 진행 중: 단계 0~9 (스키마 · 코드값 · 지표 정의 · L2 결과 · 관련 테이블 · 예시 · 재시도 · 결과 검증) — L3 프로세스 문서
- 원가: 질문 1건 평균 ₩41 (L3가 전체의 98%), 캐시 히트 ₩0, 상위 10% ₩177+ (판매가 초과)
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

## 이식 위치 (레포 대조 후 확정)

| 기준 코드 | l3-R-D 이식 위치 (예상) | 상태 |
|---|---|---|
| `build_match_report` | 경기 종료 이벤트 컨슈머 (Kafka 트리거 있음 — 대화 레이어 구조 §6) | 대조 필요 |
| `plan_lenses` · `assemble` | 쿼리 실행 결과를 L4로 넘기는 직전 | 대조 필요 |
| `NarrativeStore.match` | Postgres 조회 함수로 교체 (sql/002 쿼리) | 대조 필요 |
| `source-mapping.ts` | `INTENTS` 를 읽도록 변경 (team_compare · matchup_pattern 매핑 추가) | 대조 필요 |

## 수용 기준

- [ ] 목업 Q1 데이터로 변곡점 24:00 · 스윙 Top3 · 데스 분해 46/36/18 (`tests/test_l3.py`)
- [ ] Worlds 4강·결승 경기 배치 실행 → match_report_lens 행 생성
- [ ] 배치 lens 만 쓰는 질문은 query_cost 로그의 sonnetCalls = 0
- [ ] 정답셋에 해석 카테고리 '왜' 질문 20건 이상 추가
- [ ] 0행 결과는 캐시에 저장하지 않는다 (현재 L3 진단의 문제 — 별건이지만 같이 확인)
