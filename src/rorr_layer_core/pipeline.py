"""L2 → L3 → L4 한 번에 돌리는 기준 파이프라인 (데모·테스트용).

운영에서는 층마다 다른 레포·프로세스에서 돈다:
- L2: Jev 라우터 (/route, 레포 미확인 — D-013) 뒤에 l2.route_v2.enrich
- L3: rorr-backend-ai chat.service 쿼리 실행 뒤에 l3.bundle.assemble (+ 경기 종료 배치 l3.match_report)
- L4: piecomp/rorr-ask-renderer formatter 뒤에 l4.envelope.build
"""
from __future__ import annotations

from datetime import date
from typing import Any, Optional

from .contracts import AnswerEnvelope, L3Bundle
from .l2.route_v2 import enrich
from .l3.bundle import assemble
from .l3.match_report import build_match_report
from .l3.narrative import NarrativeFact, NarrativeStore
from .l4.envelope import build


def run_bundle(fixture: dict[str, Any], today: Optional[date] = None) -> L3Bundle:
    """L2 → L3 까지. 웹 리포트(build)와 서하(muse_cue)가 같은 묶음에서 갈라진다."""
    game = fixture.get("game")
    route = enrich(fixture["raw_route"], fixture["question"], fixture.get("page_context"),
                   has_match_context=game is not None)

    report = None
    if game:
        report = build_match_report(game["game_id"], game["subject_side"],
                                    [tuple(x) for x in game["winprob"]], game["swings"], game.get("key_death"))

    store = NarrativeStore(NarrativeFact(**{k: v for k, v in n.items()}) for n in fixture.get("narratives", []))
    ids = {r.id for r in route.entity_refs}
    narratives = store.match(ids, leagues={"LPL"}, scope="worlds", today=today)

    bundle = assemble(route, fixture.get("facts_kind"), fixture.get("facts_rows", []),
                      facts_meta=fixture.get("facts_meta"), report=report, narratives=narratives,
                      teams=(game or {}).get("teams", {}), swing_labels=(game or {}).get("swing_labels"),
                      cue_ref=(game or {}).get("game_id"))
    return bundle


def run(fixture: dict[str, Any], draft_key: str = "draft_good", entry: str = "typed",
        today: Optional[date] = None) -> AnswerEnvelope:
    return build(run_bundle(fixture, today), fixture.get(draft_key, {}), entry=entry)
