"""경기 종료 배치 — 해설형 답의 RORR 분석을 미리 계산한다 (D-006).

왜 배치인가
- L3 원가의 98%가 Sonnet 쿼리 생성(평균 ₩41, 상위 10%는 ₩177+로 판매가 ₩120 초과).
- "왜 졌어?"류는 같은 경기에 수천 명이 같은 걸 묻는다 → 경기당 1번 계산해 저장하고,
  질문 시점엔 match_report_lens 를 키로 읽기만 한다 (원가 ≈ ₩0).

입력은 모두 query 조회 가이드의 기존 뷰에서 나온다.
- 한타 승률: win_probability_frame (이름과 달리 '한타 승률' 테이블, 이름 변경 예정)
- 자원 스윙: v_objective_swing + obj_intensity_weight
- 데스 분해: v_kill_damage_breakdown
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

PROB_MIN, PROB_MAX = 5.0, 95.0   # 휴리스틱 지수라 극단값 표시 금지 (query 조회 가이드 Q3)


def clamp_prob(p: float) -> float:
    return max(PROB_MIN, min(PROB_MAX, p))


def ema(values: list[float], alpha: float = 0.4) -> list[float]:
    out: list[float] = []
    for v in values:
        out.append(v if not out else alpha * v + (1 - alpha) * out[-1])
    return out


@dataclass
class TurningPoint:
    t_sec: int           # 변화가 끝난 시각 (교전 결과가 반영된 시점) — 화면 표기는 이 시각
    from_sec: int        # 변화가 시작된 시각
    before: float
    after: float
    drop: float          # 주어 팀 기준 하락폭(%p). 음수면 상승


def turning_points(series: list[tuple[int, float]], window_sec: int = 60, min_change: float = 20.0,
                   max_points: int = 2) -> list[TurningPoint]:
    """한타 승률 시계열(초, 주어 팀 승률 %)에서 window 안에 min_change 이상 움직인 지점.

    같은 교전이 여러 번 잡히지 않게 window 안의 후보는 가장 큰 것 하나만 남긴다.
    """
    pts = sorted(series)
    cands: list[TurningPoint] = []
    j = 0
    for i, (t, p) in enumerate(pts):
        while j < len(pts) and pts[j][0] - t <= window_sec:
            j += 1
        later = pts[i:j]
        if not later:
            continue
        lo = min(later, key=lambda x: x[1])
        hi = max(later, key=lambda x: x[1])
        for end in (lo, hi):
            change = p - end[1]
            if abs(change) >= min_change:
                cands.append(TurningPoint(t_sec=end[0], from_sec=t, before=round(p, 1), after=round(end[1], 1),
                                          drop=round(change, 1)))
    cands.sort(key=lambda c: -abs(c.drop))
    picked: list[TurningPoint] = []
    for c in cands:
        if all(abs(c.t_sec - k.t_sec) > window_sec for k in picked):
            picked.append(c)
        if len(picked) == max_points:
            break
    return sorted(picked, key=lambda c: c.t_sec)


def top_swings(rows: Iterable[dict[str, Any]], subject_side: int, k: int = 3) -> list[dict[str, Any]]:
    """v_objective_swing 행 → 흐름을 가장 바꾼 오브젝트 Top k.

    impact = swing_gold_60s × intensity, 부호는 '주어 팀' 기준으로 뒤집는다
    (뷰는 획득팀 관점 — 상대가 먹은 오브젝트는 주어 팀에 음수).
    """
    out = []
    for r in rows:
        w = r.get("intensity") or 1.0
        impact = r["swing_gold_60s"] * w
        if int(r["side"]) != subject_side:
            impact = -impact
        out.append({**r, "impact": round(impact)})
    out.sort(key=lambda r: -abs(r["impact"]))
    return out[:k]


def death_breakdown(rows: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """v_kill_damage_breakdown(한 킬) → 가해자별 비중 + 솔로성 판정."""
    by_caster: dict[str, float] = {}
    for r in rows:
        if r.get("source") != "Champion":
            continue
        key = r.get("caster_label") or str(r.get("caster_id"))
        by_caster[key] = by_caster.get(key, 0.0) + float(r["total"])
    total = sum(by_caster.values()) or 1.0
    shares = sorted(((c, v / total) for c, v in by_caster.items()), key=lambda x: -x[1])
    top = shares[0][1] if shares else 0.0
    return {
        "total_damage": round(total),
        "shares": [{"caster": c, "share": round(s * 100)} for c, s in shares],
        "is_solo": top >= 0.8,  # 단일 가해자 80% 이상이면 실질 솔로킬
    }


def fmt_clock(sec: int) -> str:
    return f"{sec // 60}:{sec % 60:02d}"


def build_match_report(game_id: str, subject_side: int, winprob: list[tuple[int, float]],
                       swings: list[dict[str, Any]], key_death: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """match_report_lens 1행 (sql/001_match_report_lens.sql). 팀별로 2행 저장한다 (subject_side 100/200)."""
    shown = [(t, clamp_prob(p)) for t, p in winprob]
    tps = turning_points(shown)
    return {
        "game_id": game_id,
        "subject_side": subject_side,
        "winprob_curve": [{"t": t, "p": round(p, 1)} for t, p in shown],
        "turning_points": [{"t": tp.t_sec, "from": tp.from_sec, "clock": fmt_clock(tp.t_sec),
                            "before": tp.before, "after": tp.after}
                           for tp in tps],
        "objective_swing": top_swings(swings, subject_side),
        "death_breakdown": death_breakdown(key_death) if key_death else None,
        "report_version": "mr-v1",
    }
