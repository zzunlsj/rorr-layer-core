"""Energy 차감 규칙 (방향성 §3 · 제안안, 확정 전).

- 질문 1개 = 1 Energy (약 ₩120). 답변이 완료된 뒤 차감한다.
- 0 Energy: 데이터 없음 · L3 실패 · LoL e스포츠 밖 · 되묻기 · 시스템 오류
- 무료: 추천 질문(캐시 히트) · 답변 안 탭(드릴다운) · 근거 · 다시 보기
- 서하는 충전을 권하지 않는다 (no_dependency) — 이 모듈은 문구를 만들지 않는다.

차감 실행 위치는 백엔드(웹 입구). L2·L3·L4는 outcome 만 정하고 Energy를 직접 건드리지 않는다.
"""
from __future__ import annotations

PRICE_KRW = 120

OUTCOMES = {
    "answered": 1,
    "no_data": 0,
    "l3_failed": 0,
    "off_domain": 0,
    "clarify": 0,
    "system_error": 0,
}

FREE_ENTRY = {"recommended", "drilldown", "evidence", "replay"}


def charge(outcome: str, entry: str = "typed") -> dict[str, object]:
    """outcome(L3Bundle.outcome) + 진입 경로 → 차감 결정."""
    if entry in FREE_ENTRY:
        return {"cost": 0, "charged": False, "reason": f"free:{entry}"}
    cost = OUTCOMES.get(outcome, 0)
    return {"cost": cost, "charged": cost > 0, "reason": outcome}


def margin_krw(cost_krw: float) -> float:
    """질문 1건 마진. L3 원가 p90(₩177+)이면 음수 — 사전 계산·캐시가 필요한 이유."""
    return PRICE_KRW - cost_krw
