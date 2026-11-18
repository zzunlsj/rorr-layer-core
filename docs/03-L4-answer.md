# 03. L4 — 생성·표현 층

담당 레포: `piecomp/rorr-ask-renderer` (`formatter.py` · `prompts.py` 가 이 레포에 있다 · 브랜치 `dev` → `prod`) · 기준 코드: `src/rorr_layer_core/l4/`

## 지금 (2026-11-12 L4 마일스톤 완료 기준)

- Haiku 단일 호출 · `emit_viz` 도구 강제 · 프롬프트 캐시 → 호출당 ≈ ₩0.6 (실측)
- 코드가 kind feasibility · 숫자 재바인딩 · 이질 문자 가드

### 실제 코드 (`rorr-ask-renderer` `dev` `9e8ebe7`, 2026-11-18 대조 — 위 Notion 기준과 다른 점)

- **kind 는 3종**이다: `card` · `ranking` · `compare` (데이터 '모양' 기준). `table` · `text` 는 코드 전용 폴백. 의미별 35~37종은 폐기됐다 (`prompts.py KIND_ENUM`, `kind.md`).
- **intent 는 힌트일 뿐**이다. kind 는 q·a 로 정하고 intent 가 없어도 진행한다 (`contract.md`).
- 모델: 코드 기본값은 Haiku 5.5, **배포 설정은 Haiku 4.5** (`BEDROCK_MODEL_ID` — `rorr-backend-ai` `deploy-*.yml`. 렌더러는 AI 서버와 같은 컨테이너에서 돈다) · **temperature 미설정** · **few-shot 제거** · `max_tokens` 4096.
- 요청은 AI 서버의 `GenRequest` — `app.to_l3()` 가 `intent.type` · `retrieval.qa[0].{q, a}` · `meta.lang` 만 꺼낸다. 응답은 `{title, text, viz}` 이고 `viz` = `{kind, title, text, …kind 필드}`.
- `text` 는 **숫자를 인용하는 상세 답변**이다. 숫자 검사(`numbers_grounded`)는 구조 값(`stats/rows` 의 `value`, `entities` 의 `values`)만 하고 **`text` 프로즈 숫자는 검사하지 않는다.**
- 한국어 · 영어 2판 (`meta.lang`, `system_for`).
- 이 레포는 **봉투까지만** 만든다. 화면 렌더는 웹 프런트 레포다.

## 문제 (faker 질의 로그 2026-11-09)

| 가드레일 | 로그에서 나온 문장 |
|---|---|
| G1 주어 관점 | "졌어?" → "네, BLG는 이 경기에서 이겼어요" |
| G2 게임 시간 raw | "1395635초 무렵" |
| G3 진영 번호 | "100 측 / 200 측" |
| G4 라벨 없는 지표 | "총 39 (분당 1.21, 플러스 0.3)" |
| G5 개수 불일치 | "최근 5경기" + 표 6행 |
| G6 raw 덤프 | 이벤트 표 66행 |
| 표기 | "화학 공학 용" |

## v2 변경

### 1) 역할 분리 유지 + 문장 도구 추가 — `l4/prompt.py`
- 기존 `emit_viz`(사실 카드 kind)는 그대로.
- 해설형 intent일 때 `emit_answer` 로 문장만 받는다: `lead · sub · lens_insights{lens_id: 한 줄} · next[]`. 서하 대사(`muse`)는 받지 않는다 — 별도 Muse 메시지 (D-026).
- 시스템 프롬프트에 **주어 관점 · '왜'면 갈린 지점 · 지표 이름 필수 · 서사 생성 금지** 규칙.
- 1회 호출로 합칠지(emit_viz 스키마 확장) 2회로 나눌지는 D-008 — 캐시 prefix 크기와 지연으로 결정.

### 2) 표기 사전 — `l4/glossary.py`
- `fmt_game_time(ms)` → mm:ss · `side_to_team` → 팀 코드 · `DRAGON_KO`(raw `water` 포함) · `METRICS`(이름 · 기준 · 단위).
- `normalize_text` 는 LLM 문장에 섞인 raw 표기를 사람 표기로만 바꾼다 (의미 변경 없음).

### 3) 가드레일 — `l4/guardrails.py`
| 코드 | severity | 걸리면 |
|---|---|---|
| G1 주어 관점 | block | 템플릿 결론으로 교체 (`template_lead`, 숫자 없음) |
| G2·G3·G7 raw 시간·진영·이질 문자 | block | normalize 후에도 남으면 해당 insight 제거 |
| G4 라벨·기준 없는 지표 | block | 해당 lens 제거 |
| G5 개수 불일치 | block | 결론 교체 |
| G6 표 10행 초과 | warn | 10행 + 접기(`collapsed_rows`) |
| G8 서하 숫자·지표명 | block | 봉투 검사에서 빠졌다 — `check_muse` 는 Muse 메시지를 만드는 페르소나 경로의 출력 검사용으로 남긴다 (D-026) |
| G9 등록 안 된 서사 | block | 해당 history 제거 |
| G10 유료인데 분석 없음 | warn | 기록만 (D-009 미결) |

위반은 `violations[]` 로 봉투에 남긴다 → 대화레이어 파이프라인 로그·L3 테스트 DB에 그대로 적재해 집계.

### 4) AnswerEnvelope ask-v2.0 — `l4/envelope.py` · `contracts/answer_envelope.schema.json`
- 숫자·표·lens 값·서사 문장은 **L3Bundle 에서만**. LLM 초안의 숫자는 쓰지 않는다.
- lens 마다 `metric_label · metric_basis · unit` 을 붙인다 → 웹은 이 값으로 "LwRC+ · 같은 포지션 평균 = 100" 칩을 그린다.
- `next[].energy`: 드릴다운 0, 새 질문 1 → 목업의 ⚡1 / 무료 표시.

### 5) 웹 렌더 (웹 프런트 레포 — `rorr-ask-renderer` 아님)
| 봉투 필드 | 목업 컴포넌트 | 신규/기존 |
|---|---|---|
| lead | 결론 헤드라인 + 보충 | 신규 |
| history | 노란 '역대 맥락' 블록 + "2026 이전 데이터 연결 예정" 칩 | 신규 |
| facts | 기존 kind 카드 | 기존 |
| lenses | 'RORR 분석' 카드 + 탭(무료) · 라인/막대/분해 차트 | 신규 |
| evidence · next | 근거 칩 · 후속 질문(⚡ 표시). 서하 반응은 봉투 밖 — 별도 Muse 메시지 (D-025) | 신규 |
| energy · data_scope_label | 영수증(−1 Energy · 답변 완료 후 차감) · "2026 데이터 기준" | 신규 |

## 이식 위치 (2026-11-18 대조)

| 기준 코드 | `rorr-ask-renderer` 이식 위치 | 상태 |
|---|---|---|
| `l4/glossary.py` `fmt_game_time` · `side_to_team` · `DRAGON_KO` | `formatter.py` `_cell_value` · `_mmss` · `_SIDE_LABELS` · `_EVENT_LABELS` 와 **합친다** (같은 일을 하는 코드가 이미 있음) + `labels.md` | ✅ 위치 확인 · 규칙 충돌 있음 (D-017) |
| `l4/glossary.py` `METRICS` | 새 모듈. 지금은 컬럼 라벨 사전(`_COL_LABELS`)과 `_lwrc` 만 있고 지표 '기준' 은 없다 | ✅ 위치 확인 |
| `l4/glossary.py` `normalize_text` | `formatter.formalize()` — draft 를 받은 직후 `text` 에 적용. 지금 `text` 는 프롬프트 규칙으로만 통제된다 | ✅ 위치 확인 |
| `l4/guardrails.py` G1~G10 | `formatter.formalize()` 의 안전벨트 분기(`fillable` · `numbers_grounded` · `_downgrade`) 뒤 | ✅ 위치 확인 |
| `l4/prompt.py` `emit_answer` | `prompts.py` (`SYSTEM_HEAD` · `EMIT_VIZ_TOOL` 옆) + 영어판 미러 | ✅ 위치 확인 · D-008 |
| `l4/envelope.py` `build` | `app.py render()` 의 응답 조립 — 지금은 `{title, text, viz}` | ✅ 위치 확인 · 계약 미결 (D-015 · D-016) |

`prompts.py` 를 바꾸면 그 레포 규칙대로 `kind.md` · `contract.md` · `prompt.md` 정리본도 같이 고쳐야 한다 (`rorr-ask-renderer/CLAUDE.md`).

### 가드레일 ↔ 이미 있는 코드

| 가드레일 | 현행 `rorr-ask-renderer` | 남은 틈 |
|---|---|---|
| G2 게임 시간 raw | 표 셀은 `_cell_value` 가 ms → 분:초. `text` 는 프롬프트 규칙만 | `text` 프로즈 (faker 로그 "1395635초" 는 여기) |
| G3 진영 번호 | 표 셀 `100/200` → **블루/레드**. `text` 는 프롬프트 규칙만 | `text` 프로즈 · 팀 코드로 바꿀지는 D-017 |
| G4 라벨 없는 지표 | 컬럼 라벨 사전 · `wge` → `LwRC` | 지표 '기준' 표기 없음 |
| G5 개수 불일치 | 프롬프트 '집계·세기 금지' 규칙만 | 코드 검사 없음 |
| G6 표 10행 초과 | **정반대** — 폴백 표는 "전 행, 자르지 않음" (`_to_table`, PR `fix/large-table-rendering`) | D-017 |
| G7 이질 문자 | 프롬프트 규칙 5 (한자·가나·키릴 금지) | 코드 검사 없음 |
| 숫자 창작 | `numbers_grounded` — 구조 값만 | `text` 프로즈 숫자 |
| G1 · G9 · G10 | 없음 (주어·서사·Energy 개념이 L4 입력에 없다) | L3Bundle 전달이 먼저 (D-016) |

## 수용 기준

- [ ] faker 로그 문장 4종이 가드레일에 걸린다 (`tests/test_l4.py`)
- [ ] 목업 Q1 정상 초안 → 위반 0 · lens 3개 모두 라벨 있음
- [ ] 나쁜 초안 → 결론 "T1은 …"으로 교체 · 서하 반응 제거
- [ ] 호출당 L4 원가 ≤ ₩3 유지 (캐시 히트 기준)
- [ ] 봉투가 `contracts/answer_envelope.schema.json` 을 통과
