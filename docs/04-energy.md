# 04. Energy — 질문 1개 = 1 Energy (약 ₩120)

기준 코드: `src/rorr_layer_core/energy.py` · 실행 위치: 백엔드(웹 입구). L2·L3·L4는 `outcome` 만 정한다.

## 규칙 (제안 — docs/decisions.md D-009 에서 확정)

| 상황 | Energy | 판단 근거 |
|---|---|---|
| 답변 완료 | 1 | `L3Bundle.outcome = answered` |
| 데이터 없음 · L3 실패 · 시스템 오류 | 0 | `no_data · l3_failed · system_error` |
| LoL e스포츠 밖 질문 | 0 | L2 `path ≠ answer`, `null_reason ∈ {off_domain, not_answered}` |
| 되묻기 ("누구 말하는 거야?") | 0 | `clarify` |
| 추천 질문 · 답변 안 탭 · 근거 · 다시 보기 | 0 | 진입 경로 `recommended · drilldown · evidence · replay` |

- 차감 시점: 봉투를 웹에 보낸 뒤. 스트리밍이면 card 파트 전송 완료 시점.
- 화면: 입력창 "질문 ⚡1", 질문 아래 "−1 Energy · 답변 완료 후 차감됨", 실패 시 "Energy는 차감되지 않았어요".
- 서하는 충전·Boost를 권하지 않는다 (no_dependency).

## 경제성

| 원가 | 마진 (₩120 기준) |
|---|---|
| 배치 lens · 캐시 히트 ≈ ₩1~4 | ≈ ₩116 |
| 쿼리 신규 생성 평균 ≈ ₩42 | ≈ ₩78 |
| 쿼리 신규 생성 상위 10% ≈ ₩177+ | **음수** |

→ 마진의 관건은 비싼 꼬리를 **경기 종료 배치 + 쿼리 캐시**로 줄이는 것. `energy.margin_krw` 로 로그 집계.

## 지금 코드와 다른 점 (2026-11-18 대조)

`rorr-backend-api-v2` `affect.controller.ts` 는 **AI 호출 전에 1 을 먼저 빼고**, 답 `text` 가 비었거나 엔진이 `l4-web-fallback` 일 때만 돌려준다.
그래서 코드상 **데이터 없음 안내 카드 · 롤 밖 질문은 차감되는 것으로 읽힌다** (운영 로그 확인 필요). 추천 질문 칩은 무료다.
바꿀 곳과 표는 `docs/05-current-vs-target.md` §6 · 결정은 D-023.
