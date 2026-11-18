"""L3 → L4 묶음(L3Bundle) 조립.

L3의 기존 일(쿼리 생성·실행)은 그대로 두고, 그 결과에
① 사실 행(facts) ② RORR 분석(lens) ③ 서사 카드 ④ 데이터 범위 ⑤ 출처 ⑥ 원가 ⑦ outcome 을 붙인다.
outcome 은 Energy 차감 판단에 쓰인다 (energy.py).
"""
from __future__ import annotations

from typing import Any, Optional

from ..contracts import L3Bundle, Lens, LensValue, NarrativeRef, RouteResult
from .lenses import LENSES, estimated_cost_krw, plan_lenses


def lens_from_report(lens_id: str, report: dict[str, Any], labels: Optional[dict[str, str]] = None) -> Optional[Lens]:
    """match_report_lens 행 → Lens. 배치가 없는 경기면 None."""
    spec = LENSES[lens_id]
    labels = labels or {}
    if lens_id == "winprob_curve" and report.get("winprob_curve"):
        return Lens(lens_id, spec.title, spec.metric,
                    series=[LensValue(label=str(pt["t"]), value=pt["p"], unit="%") for pt in report["winprob_curve"]],
                    markers=report.get("turning_points", []), sources=list(spec.sources))
    if lens_id == "objective_swing" and report.get("objective_swing"):
        return Lens(lens_id, spec.title, spec.metric,
                    series=[LensValue(label=labels.get(str(r.get("sequence_index")), r.get("category", "")),
                                      value=r["impact"], unit="gold") for r in report["objective_swing"]],
                    sources=list(spec.sources))
    if lens_id == "death_breakdown" and report.get("death_breakdown"):
        d = report["death_breakdown"]
        return Lens(lens_id, spec.title, spec.metric,
                    series=[LensValue(label=s["caster"], value=s["share"], unit="%") for s in d["shares"]],
                    markers=[{"is_solo": d["is_solo"], "total_damage": d["total_damage"]}],
                    sources=list(spec.sources))
    return None


def assemble(route: RouteResult, facts_kind: Optional[str], facts_rows: list[dict[str, Any]],
             facts_meta: Optional[dict[str, Any]] = None, report: Optional[dict[str, Any]] = None,
             extra_lenses: Optional[list[Lens]] = None, narratives: Optional[list[NarrativeRef]] = None,
             teams: Optional[dict[str, str]] = None, cache_hit: bool = False,
             swing_labels: Optional[dict[str, str]] = None) -> L3Bundle:
    if route.path != "answer":
        outcome = "off_domain" if route.null_reason in ("off_domain", "not_answered") else "clarify"
        return L3Bundle(route=route, facts_kind=None, outcome=outcome)

    specs = plan_lenses(route.intent, has_game=report is not None)
    lenses: list[Lens] = []
    for spec in specs:
        if spec.precomputed and report is not None:
            lens = lens_from_report(spec.lens_id, report, swing_labels)
            if lens:
                lenses.append(lens)
    lenses.extend(extra_lenses or [])

    outcome = "answered" if (facts_rows or facts_meta or lenses) else "no_data"
    sources = sorted({s for l in lenses for s in l.sources})
    return L3Bundle(
        route=route, facts_kind=facts_kind, facts_rows=facts_rows, facts_meta=facts_meta or {},
        lenses=lenses, narratives=narratives or [], teams=teams or {}, data_scope="2026",
        sources=sources, cost_krw=estimated_cost_krw(specs, cache_hit), outcome=outcome,
    )
