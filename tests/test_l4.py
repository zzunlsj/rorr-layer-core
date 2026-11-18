from rorr_layer_core.contracts import EntityRef, L3Bundle, RouteResult, Subject
from rorr_layer_core.l4 import fmt_game_time, normalize_text
from rorr_layer_core.l4.envelope import topic_particle
from rorr_layer_core.l4.guardrails import check_counts, check_muse, check_subject, check_text
from rorr_layer_core.pipeline import run

TEAMS = {"100": "T1", "200": "BLG"}


def test_glossary_fixes_faker_log_q3(faker_log):
    out = normalize_text(faker_log["q3"]["answer"], TEAMS)
    assert "1395635초" not in out and "23:15" in out          # ms → mm:ss
    assert "200 측" not in out and "100 측" not in out
    assert "화학공학 드래곤" in out
    assert check_text("lead", out) == []


def test_fmt_game_time():
    assert fmt_game_time(1931155) == "32:11"


def test_g1_catches_faker_log_q2(faker_log):
    subj = Subject(EntityRef("faker", "player", "1", "Faker"), "loss", EntityRef("BLG", "team", "2", "BLG"))
    codes = {v.code for v in check_subject(faker_log["q2"]["answer_lead"], subj)}
    assert codes == {"G1"}


def test_g5_catches_faker_log_q1(faker_log):
    v = check_counts([faker_log["q1"]["answer"]], faker_log["q1"]["table_rows"])
    assert v and v[0].code == "G5"


def test_g8_muse_numbers():
    assert check_muse("한타 승률 22%라니!", ["한타 승률"])
    assert not check_muse("아… 바론 앞 그 한타, 숨 멈췄어.", ["한타 승률"])


def test_particle():
    assert topic_particle("T1") == "은" and topic_particle("BLG") == "는" and topic_particle("젠지") == "는"


def test_pipeline_good_draft(q1):
    env = run(q1).to_dict()
    assert env["violations"] == []
    assert env["energy"] == {"cost": 1, "charged": True, "reason": "answered"}
    assert [l["lens_id"] for l in env["lenses"]] == ["winprob_curve", "objective_swing", "death_breakdown"]
    assert all(l["metric_label"] for l in env["lenses"])
    assert env["history"][0]["fact_id"] == "nf-0001"
    assert env["data_scope_label"] == "2026 데이터 기준"
    assert [n["energy"] for n in env["next"]] == [0, 1, 1]


def test_pipeline_bad_draft_is_repaired(q1):
    env = run(q1, "draft_bad").to_dict()
    codes = {v["code"] for v in env["violations"]}
    assert {"G1", "G8"} <= codes
    assert env["lead"]["text"].startswith("T1은") and env["muse"] is None


def test_no_data_is_free():
    r = RouteResult(path="answer", domain="esports", topic="team", intent="team_stat")
    from rorr_layer_core.l4.envelope import build
    env = build(L3Bundle(route=r, facts_kind=None, outcome="no_data"), {})
    assert env.energy["cost"] == 0


def test_drilldown_is_free(q1):
    assert run(q1, entry="drilldown").energy["cost"] == 0
