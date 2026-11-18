"""L4 — L3Bundle + LLM 초안(draft) → AnswerEnvelope (웹이 렌더하는 봉투).

순서
1. draft 문장을 표기 사전으로 정규화 (glossary.normalize_text)
2. 숫자·표·lens 값은 bundle 에서만 가져온다 (draft 숫자 신뢰 안 함)
3. lens 마다 지표 라벨·기준을 붙인다 (G4)
4. 서사는 bundle.narratives 카드 문장 그대로 (G9)
5. Energy 결정 (energy.charge)
6. 가드레일 실행 → block 위반은 블록 교체·제거, warn 은 기록
"""
from __future__ import annotations

from dataclasses import asdict
from typing import Any, Optional

from ..contracts import CONTRACT_VERSION, AnswerEnvelope, L3Bundle
from ..energy import charge
from . import guardrails
from .glossary import METRICS, normalize_text

DATA_SCOPE_LABEL = {"2026": "2026 데이터 기준"}


def _lens_dict(lens, insight: Optional[str], teams: dict[str, str]) -> dict[str, Any]:
    name, basis, unit = METRICS.get(lens.metric, (None, None, ""))
    d = asdict(lens)
    d["insight"] = normalize_text(insight, teams) if insight else None
    d["metric_label"] = name
    d["metric_basis"] = basis
    d["unit"] = unit
    return d


def _subject_name(bundle: L3Bundle) -> str:
    s = bundle.route.subject
    if s and s.entity:
        return s.entity.display or s.entity.name
    return ""


def topic_particle(word: str) -> str:
    """은/는 — 한글은 받침, 영문·숫자는 읽는 소리 기준 (T1 → 티원은)."""
    if not word:
        return "는"
    ch = word[-1]
    if "가" <= ch <= "힣":
        return "은" if (ord(ch) - 0xAC00) % 28 else "는"
    return "은" if ch.lower() in "0136781lmn" else "는"


def template_lead(bundle: L3Bundle) -> str:
    """LLM 결론이 가드레일에 걸렸을 때 쓰는 안전한 템플릿 결론 (숫자 없음)."""
    who = _subject_name(bundle)
    tp = next((l for l in bundle.lenses if l.lens_id == "winprob_curve" and l.markers), None)
    if who and tp:
        return f"{who}{topic_particle(who)} {tp.markers[0].get('clock', '')} 교전에서 흐름을 넘겨줬어요."
    return f"{who} 관련 결과를 정리했어요." if who else "결과를 정리했어요."


def build(bundle: L3Bundle, draft: dict[str, Any], entry: str = "typed") -> AnswerEnvelope:
    teams = bundle.teams
    energy = charge(bundle.outcome, entry)

    if bundle.outcome != "answered":
        return AnswerEnvelope(
            version=CONTRACT_VERSION,
            lead={"text": "지금 데이터로는 답하기 어려워요.", "sub": "Energy는 차감되지 않았어요."},
            history=[], facts=None, lenses=[], evidence=[], muse=None,
            next=[{"text": t, "energy": 0} for t in ("결승 일정 언제야?", "LwRC+가 뭐야?")],
            energy=energy, data_scope_label="")

    insights = draft.get("lens_insights", {})
    env: dict[str, Any] = {
        "lead": {"text": normalize_text(draft.get("lead", ""), teams),
                 "sub": normalize_text(draft.get("sub", ""), teams)},
        "history": [{"fact_id": n.fact_id, "text": n.text, "basis": n.basis, "source": n.source}
                    for n in bundle.narratives],
        "facts": {"kind": bundle.facts_kind, "rows": bundle.facts_rows[: guardrails.MAX_FACT_ROWS],
                  "collapsed_rows": max(0, len(bundle.facts_rows) - guardrails.MAX_FACT_ROWS),
                  "meta": bundle.facts_meta} if bundle.facts_kind else None,
        "lenses": [_lens_dict(l, insights.get(l.lens_id), teams) for l in bundle.lenses],
        "evidence": bundle.sources,
        "muse": {"text": draft["muse"]} if draft.get("muse") else None,
        "next": [{"text": n["text"], "energy": 0 if n.get("drilldown") else 1} for n in draft.get("next", [])],
        "energy": energy,
    }

    violations = guardrails.run_all(env, bundle)
    blocks = {v.block for v in violations if v.severity == "block"}
    if "lead" in blocks:
        env["lead"] = {"text": template_lead(bundle), "sub": ""}
    if "muse" in blocks:
        env["muse"] = None
    if "history" in blocks:
        allowed = {n.fact_id for n in bundle.narratives}
        env["history"] = [h for h in env["history"] if h["fact_id"] in allowed]
    if "lens" in blocks:
        env["lenses"] = [l for l in env["lenses"] if l["metric_label"]]
        for l in env["lenses"]:
            if l["insight"] and guardrails.check_text("lens", l["insight"]):
                l["insight"] = None

    return AnswerEnvelope(
        version=CONTRACT_VERSION, lead=env["lead"], history=env["history"], facts=env["facts"],
        lenses=env["lenses"], evidence=env["evidence"], muse=env["muse"], next=env["next"],
        energy=energy, data_scope_label=DATA_SCOPE_LABEL.get(bundle.data_scope, bundle.data_scope),
        violations=[{"code": v.code, "block": v.block, "message": v.message, "severity": v.severity}
                    for v in violations],
    )
