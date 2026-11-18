import json
import pathlib

from rorr_layer_core.contracts import Lens, LensValue, MuseMessage, RouteResult
from rorr_layer_core.l3 import build_muse_cue
from rorr_layer_core.muse import check_message
from rorr_layer_core.pipeline import run, run_bundle

SCHEMAS = pathlib.Path(__file__).resolve().parents[1] / "contracts"


def _numbers(value):
    """dict 안의 숫자형 값 (bool 제외)."""
    if isinstance(value, dict):
        return [n for v in value.values() for n in _numbers(v)]
    return [value] if isinstance(value, (int, float)) and not isinstance(value, bool) else []


def test_cue_from_q1(q1):
    cue = run_bundle(q1).muse_cue.to_dict()
    assert cue["polarity"] == "loss" and cue["subject"]["display"] == "T1"
    assert (cue["turning"], cue["phase"], cue["trend"]) == ("teamfight", "mid", "sudden_drop")
    assert cue["has_narrative"] and cue["has_report"] and cue["ref"] == "WORLDS2026_SF_T1_BLG_G4"


def test_cue_has_no_numbers_and_matches_schema(q1):
    cue = run_bundle(q1).muse_cue.to_dict()
    assert _numbers(cue) == []
    schema = json.loads((SCHEMAS / "muse_cue.schema.json").read_text())
    assert set(cue) <= set(schema["properties"]) and set(schema["required"]) <= set(cue)
    for key in ("outcome", "polarity", "turning", "phase", "trend"):
        assert cue[key] in schema["properties"][key]["enum"]


def test_cue_does_not_reach_web_envelope(q1):
    assert "muse_cue" not in run(q1).to_dict()


def test_cue_without_turning_point_uses_slow_trend():
    route = RouteResult(path="answer", domain="esports", topic="team", intent="match_review")
    curve = Lens("winprob_curve", "한타 승률 흐름", "teamfight_win_prob",
                 series=[LensValue("0", 55, "%"), LensValue("1800", 30, "%")])
    cue = build_muse_cue(route, [curve], "answered")
    assert (cue.turning, cue.phase, cue.trend) == ("none", "unknown", "slow_drop")


def test_cue_when_not_answered():
    route = RouteResult(path="answer", domain="esports", topic="team", intent="match_review")
    cue = build_muse_cue(route, [], "no_data")
    assert cue.turning == "unknown" and not cue.has_report


def test_message_rules(q1):
    cue = run_bundle(q1).muse_cue
    ok = MuseMessage(kind="echo", surface="web_sd", text="아… T1 그 한타, 나도 보다가 숨 멈췄어.", cue_ref=cue.ref)
    assert check_message(ok, cue) == []
    codes = lambda m: {v.code for v in check_message(m, cue)}  # noqa: E731
    assert codes(MuseMessage(kind="echo", surface="web_sd", text="한타 승률 22%라니 너무해!", cue_ref=cue.ref)) == {"M1"}
    assert codes(MuseMessage(kind="reply", surface="extension", text="충전하고 더 물어봐!")) == {"M2"}
    assert codes(MuseMessage(kind="echo", surface="web_sd", text="아쉽다…")) == {"M3"}
    assert codes(MuseMessage(kind="proactive", surface="web_sd", text="곧 시작해!")) == {"M4"}
