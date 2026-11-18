# 01. L2 — 의도 판정 층

담당 레포: `piecomp/rorr-user-intent-router` (Jev 라우터 `/route`) · `piecomp/rorr-socket-server` (호출 · scope) — D-020 · 기준 코드: `src/rorr_layer_core/l2/`

## 지금 (2026-11-13 L2 마일스톤 완료 기준)

- Jev 판정: domain+topic 한 요청 → intent (`judge_route`), 메시지당 1.91회 · 약 $0.0002 · p50 358ms
- 정답셋 568: domain 97.5% · in_scope intent 85.0% · 거절 88.6%
- 출력: `path · domain · topic · intent · null_reason · verdict · slots{entity_refs, unresolved, metrics} · emotion`

## 문제 (Notion 문서 · faker 로그에서 확인)

| # | 문제 | 근거 |
|---|---|---|
| 1 | 질문의 주어·전제를 안 잡음 → "페이커 졌어?"에 "BLG는 이겼어요" | faker 질의 로그 Q2 |
| 2 | "왜/아쉬운 점"을 해설형으로 인식 못 함 → 연대기 나열 | faker 질의 로그 Q3 |
| 3 | intent 목록 L2 35종 vs L3 34종 (team_compare 없음) | L3 프로세스 'L2–L3 논의' — 라우터 `data/labels.json` 35종에는 `team_compare` 가 있다. L3 `source-mapping.ts` 는 legacy · RAG 경로에서만 쓰인다 |
| 4 | `null_reason` 은 소켓이 안 읽고, `verdict · path · unresolved` 는 백엔드 → AI 서버에서 끊긴다 | 코드 확인 (2026-11-18) — 소켓 `affect-api.service.ts` · 백엔드 `affect.controller.ts` |
| 5 | scope 계산이 세 곳 — 라우터 `scope.py`(계약에 안 실림) · 소켓 `scope.service.ts`(자기 어휘 목록) · AI 서버(통계 질문이면 season 강제) | 코드 확인 (2026-11-18) |

## v2 변경

### 1) intent 레지스트리 단일화 — `l2/intents.py`
- L2·L3가 같은 `INTENTS` 와 `INTENT_REGISTRY_VERSION` 을 본다.
- `team_compare` 추가, 신규 `matchup_pattern` ("왜 약해?" 류).
- intent마다 `category`(fact/interpret/live/reference) 와 기본 lens 목록 → L3가 그대로 사용.

### 2) question_form · subject — `l2/question.py` (규칙, LLM 0)
- `question_form`: why > compare > when > how > what. "왜·이유·아쉬·어디서 갈렸" → why, "어때·폼" → how.
- `subject_of`: 선수·팀 엔티티 중 주격·주제 조사(은/는/이/가)가 붙은 것 → 없으면 먼저 나온 것. 나머지 첫 후보가 상대.
- `polarity`: "졌·패배·탈락" → loss, "이겼·승리·진출" → win. L4 가드레일 G1이 이걸로 결론 관점을 검사한다.

### 3) 해설형 intent 승격 — `upgrade_intent`
| 질문 형태 | 원래 intent | → |
|---|---|---|
| why | team_record · team_form · team_stat · team_compare | matchup_pattern |
| why + 경기 맥락 | team_form · match_result | match_review |
| why | player_stat · player_form · player_champion | player_review |
| how | player_stat | player_form |

Jev 프롬프트를 바꾸지 않고 뒤에서 올린다 → Jev 호출 수·정답셋 정확도에 영향 없음. 효과가 확인되면 Jev 정답셋에도 반영.

### 4) 필드 끝까지 전달 — `l2/route_v2.py enrich()`
- `verdict · null_reason · unresolved` 를 RouteResult 에 그대로 담는다 (contracts/l2_route_v2.schema.json).
- 웹 페이지 맥락(선수 페이지 등)을 **슬롯 기본값**으로 — 주어 없는 질문을 보고 있는 선수로 채움 (덮어쓰기 아님).
- scope: 맥락 > 텍스트 > DB (D-005, 제안).

## 이식 위치 (2026-11-18 대조 — 코드 확인)

대조: `rorr-user-intent-router` `prod` `4218e90` · `rorr-socket-server` `dev` `f66dd26` · `rorr-backend-api-v2` `dev` `5830d9c`. 현황 전체는 `docs/05-current-vs-target.md` §3.

| 기준 코드 | 이식 위치 | 상태 |
|---|---|---|
| `enrich()` 순서 | `rorr-user-intent-router` `src/embedder/service.py` `_route_jev()` — `jev.to_contract()` 로 계약을 만든 직후 | ✅ 위치 확인 |
| `question_form`, `subject_of` | 같은 레포 `src/embedder/` 새 규칙 모듈 (`gate.py` · `scope.py` 와 같은 층). 계약 키는 `router.py CONTRACT_KEYS` 와 `scripts/test_contract.py` 가 고정한다 | ✅ 위치 확인 |
| `INTENTS` | `rorr-user-intent-router` `data/labels.json` (라벨 단일 진실원 · 35종) 과 맞춘다. `matchup_pattern` 은 여기에 추가, `team_champions` 는 라우터에 없다 | ✅ 위치 확인 · 불일치 1건 |
| 필드 전달 (`null_reason` · `verdict` · `path` · `unresolved`) | 소켓 `affect-api.service.ts` `RouteContract` → 백엔드 `affect.controller.ts` `/chat/generate` 본문 → `rorr-backend-ai` `chat.types.ts GenerateRequest` | ✅ 위치 확인 |
| 소켓 `scope.service.ts` 시점 어휘 | 삭제 → 라우터 `scope.py` 결과를 계약에 싣는다 | ✅ 위치 확인 · D-005 |

### 대조에서 확인된 것

- **라우터 입력은 `{text, lang}` 뿐이다.** 대화 기록 · 페이지 맥락이 `/route` 에 가지 않는다 — `enrich()` 의 페이지 맥락 기본값을 쓰려면 웹 → 소켓 → 라우터 요청에 자리가 먼저 필요하다.
- **L3 는 지금 L2 값을 덮어쓴다.** `rorr-backend-ai` `chat.service.ts generate()` 가 텍스트 정규식으로 metrics · role · intent 를 다시 추론하고, 선수/팀 + 통계 지표면 scope 를 season 으로 강제한다.
- **웹 요청에 L2 결과가 없으면 AI 서버가 직접 `/route` 를 부른다** (`withL2`, HTTP 경로). 소켓 경로와 두 갈래라 필드를 늘릴 때 양쪽을 같이 고쳐야 한다.
- **L2 → L3 연동 규칙은 아직 합의 전이다.** `l3-R-D/etc/l2_rules.md` 는 전체가 주석 처리된 초안이다. 다만 운영 L3 는 이미 L2 결과(intent · topic · scope · 엔티티 ID · metrics)를 모델에 힌트로 넘긴다 (`prompt-builder.ts buildL2Hint`).
- **정답셋의 L2 값은 옛 intent 이름이다.** `l3-R-D` `goldset/dev.json` · `final.json` 의 `l2.intent` 는 `game_state` · `victory_analysis` · `defeat_analysis` 등 — 뒤 두 개는 `INTENTS` 에도 라우터 35종에도 없다.

## 수용 기준

- [ ] faker 로그 Q2 문장 → subject=Faker, polarity=loss (`tests/test_l2.py`)
- [ ] 목업 3개 질문 → match_review / player_form / matchup_pattern
- [ ] verdict·null_reason·unresolved 가 L3 로그까지 도달
- [ ] Jev 정답셋 568 정확도 하락 없음 (후처리라 영향 없어야 함)
- [ ] 메시지당 Jev 호출 수 증가 없음
