# 03. L4 — 생성·표현 층

담당 레포: `piecomp/rorr-ask-renderer` (+ AI 서버 `formatter.py`) · 기준 코드: `src/rorr_layer_core/l4/`

## 지금 (2026-11-12 L4 마일스톤 완료 기준)

- Haiku 단일 호출 · temperature 0 · `emit_viz` 도구 강제 · kind enum · few-shot 상주 · 프롬프트 캐시 → 호출당 ≈ ₩0.6 (실측)
- 코드가 kind feasibility · 숫자 재바인딩 · 이질 문자 가드
- 카드 37 kind 중 확정 3, 나머지 '적용/수정필요'

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
- 해설형 intent일 때 `emit_answer` 로 문장만 받는다: `lead · sub · lens_insights{lens_id: 한 줄} · muse · next[]`.
- 시스템 프롬프트에 **주어 관점 · '왜'면 갈린 지점 · 지표 이름 필수 · 서사 생성 금지 · 서하 숫자 금지** 규칙.
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
| G8 서하 숫자·지표명 | block | muse 제거 |
| G9 등록 안 된 서사 | block | 해당 history 제거 |
| G10 유료인데 분석 없음 | warn | 기록만 (D-009 미결) |

위반은 `violations[]` 로 봉투에 남긴다 → 대화레이어 파이프라인 로그·L3 테스트 DB에 그대로 적재해 집계.

### 4) AnswerEnvelope ask-v2.0 — `l4/envelope.py` · `contracts/answer_envelope.schema.json`
- 숫자·표·lens 값·서사 문장은 **L3Bundle 에서만**. LLM 초안의 숫자는 쓰지 않는다.
- lens 마다 `metric_label · metric_basis · unit` 을 붙인다 → 웹은 이 값으로 "LwRC+ · 같은 포지션 평균 = 100" 칩을 그린다.
- `next[].energy`: 드릴다운 0, 새 질문 1 → 목업의 ⚡1 / 무료 표시.

### 5) 웹 렌더 (rorr-ask-renderer)
| 봉투 필드 | 목업 컴포넌트 | 신규/기존 |
|---|---|---|
| lead | 결론 헤드라인 + 보충 | 신규 |
| history | 노란 '역대 맥락' 블록 + "2026 이전 데이터 연결 예정" 칩 | 신규 |
| facts | 기존 kind 카드 | 기존 |
| lenses | 'RORR 분석' 카드 + 탭(무료) · 라인/막대/분해 차트 | 신규 |
| evidence · muse · next | 근거 칩 · 서하 반응 · 후속 질문(⚡ 표시) | 신규 |
| energy · data_scope_label | 영수증(−1 Energy · 답변 완료 후 차감) · "2026 데이터 기준" | 신규 |

## 수용 기준

- [ ] faker 로그 문장 4종이 가드레일에 걸린다 (`tests/test_l4.py`)
- [ ] 목업 Q1 정상 초안 → 위반 0 · lens 3개 모두 라벨 있음
- [ ] 나쁜 초안 → 결론 "T1은 …"으로 교체 · 서하 반응 제거
- [ ] 호출당 L4 원가 ≤ ₩3 유지 (캐시 히트 기준)
- [ ] 봉투가 `contracts/answer_envelope.schema.json` 을 통과
