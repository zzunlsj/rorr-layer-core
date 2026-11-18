# 01. L2 — 의도 판정 층

담당 레포: `piecomp/l3-R-D` (라우터) · 기준 코드: `src/rorr_layer_core/l2/`

## 지금 (2026-11-13 L2 마일스톤 완료 기준)

- Jev 판정: domain+topic 한 요청 → intent (`judge_route`), 메시지당 1.91회 · 약 $0.0002 · p50 358ms
- 정답셋 568: domain 97.5% · in_scope intent 85.0% · 거절 88.6%
- 출력: `path · domain · topic · intent · null_reason · verdict · slots{entity_refs, unresolved, metrics} · emotion`

## 문제 (Notion 문서 · faker 로그에서 확인)

| # | 문제 | 근거 |
|---|---|---|
| 1 | 질문의 주어·전제를 안 잡음 → "페이커 졌어?"에 "BLG는 이겼어요" | faker 질의 로그 Q2 |
| 2 | "왜/아쉬운 점"을 해설형으로 인식 못 함 → 연대기 나열 | faker 질의 로그 Q3 |
| 3 | intent 목록 L2 35종 vs L3 34종 (team_compare 없음) | L3 프로세스 'L2–L3 논의' |
| 4 | verdict · null_reason · unresolved 가 소켓·백엔드에서 버려짐 | L3 프로세스 'L2–L3 논의' |
| 5 | scope 계산이 소켓/L3 두 곳 (소켓 계산 → L3가 season으로 덮어씀) | L3 프로세스 · 대화 레이어 구조 §2 |

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

## 이식 위치 (레포 대조 후 확정)

| 기준 코드 | l3-R-D 이식 위치 (예상) | 상태 |
|---|---|---|
| `enrich()` 순서 | `/route` 응답 직전 (judge_route 뒤) | 대조 필요 |
| `question_form`, `subject_of` | 화행 게이트 옆 규칙 모듈 | 대조 필요 |
| `INTENTS` | L2 intent 목록 + L3 `source-mapping.ts` 가 import 하는 단일 파일 | 대조 필요 |
| 소켓 `scope.service.ts` 시점 어휘 | 삭제 → 라우터 한 곳으로 | 대조 필요 |

## 수용 기준

- [ ] faker 로그 Q2 문장 → subject=Faker, polarity=loss (`tests/test_l2.py`)
- [ ] 목업 3개 질문 → match_review / player_form / matchup_pattern
- [ ] verdict·null_reason·unresolved 가 L3 로그까지 도달
- [ ] Jev 정답셋 568 정확도 하락 없음 (후처리라 영향 없어야 함)
- [ ] 메시지당 Jev 호출 수 증가 없음
