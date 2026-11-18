# 층별 태스크 초안 (Notion 태스크 DB 등록 전 검토용)

마일스톤: **ASK RORR 답변 고도화** · 단계: P0(Worlds 결승 전후) · P1(11/15 이후) · P2 · P3
담당은 검토 후 지정. 기준 코드 경로를 같이 적었다.

## L2 — 의도 판정 (Jev 라우터 레포 — 미확인, D-013)

| # | 단계 | 태스크 | 기준 코드 | 완료 조건 |
|---|---|---|---|---|
| L2-1 | P0 | v2 후처리 `enrich()` 이식 — verdict·null_reason·unresolved 전달 | `l2/route_v2.py` | L3 로그에 세 필드 도달 |
| L2-2 | P0 | question_form · subject/극성 규칙 이식 | `l2/question.py` | faker 로그 Q2 → Faker · loss |
| L2-3 | P1 | intent 레지스트리 단일화 + team_compare · matchup_pattern | `l2/intents.py` | L2·L3 목록 버전 일치 |
| L2-4 | P1 | '왜/어때' intent 승격 + Jev 정답셋에 해설형 문장 추가 | `upgrade_intent` | 목업 질문 3개 기대 intent |
| L2-5 | P1 | 소켓 scope.service.ts 시점 어휘 제거 → 라우터 일원화 (D-005 확정 후) | — | scope 계산 1곳 |

## L3 — 컨텍스트 조립 (rorr-backend-ai · 측정은 l3-R-D)

| # | 단계 | 태스크 | 기준 코드 | 완료 조건 |
|---|---|---|---|---|
| L3-1 | P0 | match_report_lens 테이블 + 경기 종료 배치 | `l3/match_report.py`, `sql/001` | Worlds 4강·결승 행 생성 |
| L3-2 | P0 | narrative_fact 테이블 + 매칭 조회 | `l3/narrative.py`, `sql/002` | nf-0001 매칭 |
| L3-3 | P1 | lens 레지스트리 + L3Bundle(출처·원가·outcome) | `l3/lenses.py`, `l3/bundle.py` | 배치 lens 질문 sonnetCalls 0 |
| L3-4 | P1 | 정답셋에 해석 카테고리 '왜' 질문 20건+ | — | L3 테스트 DB 반영 |
| L3-5 | P1 | LwRC+ ID 매핑 후 lwrc lens 연결 | `lenses.py` lwrc_* | Q2 목업 재현 |
| L3-6 | P2 | 관계형 lens(gold_diff_by_minute · first_objective_rate · role_matchup) 쿼리 + 캐시 | `lenses.py` | Q3 목업 재현, 두 번째부터 ₩0 |
| L3-7 | P3 | 역대 시리즈·게임 결과 적재 → 서사 카드 자동 도출 | `narrative.py` auto_derived | 사람은 검수만 |

## L4 — 생성·표현 (rorr-ask-renderer `formatter.py` · `prompts.py`)

| # | 단계 | 태스크 | 기준 코드 | 완료 조건 |
|---|---|---|---|---|
| L4-1 | P0 | 표기 사전 이식 (mm:ss · 팀 코드 · 드래곤 · 지표 라벨) | `l4/glossary.py` | faker 로그 Q3 문장 정상화 |
| L4-2 | P0 | 가드레일 G1~G10 + violations 로그 적재 | `l4/guardrails.py` | faker 로그 4종 차단 |
| L4-3 | P1 | emit_answer 프롬프트 + D-008 측정 | `l4/prompt.py` | 호출당 ≤ ₩3 |
| L4-4 | P1 | AnswerEnvelope ask-v2.0 + 웹 렌더(lead · history · lens 탭 · next 비용) | `l4/envelope.py`, schema | 목업 Q1 화면 재현 |
| L4-5 | P1 | Energy 표시(잔량 · 영수증 · 실패 시 미차감 안내) | `energy.py` | 0 Energy 경로 4종 확인 |

## 공통

| # | 단계 | 태스크 | 완료 조건 |
|---|---|---|---|
| C-1 | P0 | 서사 카드 첫 묶음 등록 (T1·Gen.G·BLG 등) + nf-0001 기준 확정 | verified 카드 10장+ |
| C-2 | P1 | 백엔드 Energy 차감 · 환불 로직 | D-009 확정 규칙 반영 |
