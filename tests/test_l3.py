from datetime import date

from rorr_layer_core.l3 import NarrativeFact, NarrativeStore, death_breakdown, plan_lenses, top_swings, turning_points
from rorr_layer_core.l3.match_report import clamp_prob


def test_turning_point_found_at_baron_fight(q1):
    pts = turning_points([tuple(x) for x in q1["game"]["winprob"]])
    assert pts and pts[0].t_sec == 24 * 60 and pts[0].before > 50 and pts[0].after < 30


def test_turning_point_ignores_small_wobble():
    series = [(i * 60, 50 + (i % 3)) for i in range(30)]
    assert turning_points(series) == []


def test_clamp():
    assert clamp_prob(1) == 5 and clamp_prob(99) == 95


def test_top_swings_sign_is_subject_perspective(q1):
    top = top_swings(q1["game"]["swings"], subject_side=100)
    assert [t["impact"] for t in top] == [-3850, -1420, 1182]   # 상대가 먹은 바론은 T1에 음수


def test_death_breakdown_not_solo(q1):
    d = death_breakdown(q1["game"]["key_death"])
    assert [s["share"] for s in d["shares"]] == [46, 36, 18] and d["is_solo"] is False


def test_plan_lenses_drop_match_lenses_without_game():
    assert [s.lens_id for s in plan_lenses("match_review", has_game=True)] == \
        ["winprob_curve", "objective_swing", "death_breakdown"]
    assert plan_lenses("match_review", has_game=False) == []
    assert [s.lens_id for s in plan_lenses("player_form", has_game=False)] == ["lwrc_by_game", "lwrc_cdr"]


def _fact(**kw):
    base = dict(fact_id="nf-1", entity_a="T1", entity_b="LPL", scope="worlds", text="t", basis="b", source="s",
                status="verified")
    base.update(kw)
    return NarrativeFact(**base)


def test_narrative_only_verified_and_active():
    store = NarrativeStore([_fact(), _fact(fact_id="nf-2", status="draft"),
                            _fact(fact_id="nf-3", valid_to=date(2026, 1, 1))])
    got = store.match({"T1"}, leagues={"LPL"}, scope="worlds", today=date(2026, 11, 18), limit=5)
    assert [g.fact_id for g in got] == ["nf-1"]


def test_narrative_needs_matching_counterpart():
    store = NarrativeStore([_fact(entity_b="LCK")])
    assert store.match({"T1"}, leagues={"LPL"}) == []
