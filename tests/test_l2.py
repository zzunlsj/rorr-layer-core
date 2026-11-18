from rorr_layer_core.contracts import EntityRef
from rorr_layer_core.l2 import INTENTS, enrich, question_form, subject_of, upgrade_intent

T1 = EntityRef("T1", "team", "98767991853197861", "T1")
BLG = EntityRef("BLG", "team", "BLG_TEAM_ID", "BLG")
FAKER = EntityRef("faker", "player", "98767991747728851", "Faker")


def test_question_form():
    assert question_form("T1, BLG 4세트 왜 졌어?") == "why"
    assert question_form("이번 BLG 경기에서 어떤 점이 아쉬웠어?") == "why"
    assert question_form("페이커 이번 Worlds 폼 어때?") == "how"
    assert question_form("페이커 vs 쇼메이커 KDA") == "compare"
    assert question_form("결승 일정 언제야?") == "when"
    assert question_form("T1 미드 누구야?") == "what"


def test_subject_and_polarity_faker_log_q2():
    # 로그: "졌어?"를 물었는데 BLG 관점으로 답했다 → 주어는 Faker, 극성은 loss
    s = subject_of("faker BLG 경기는? 오늘 있었잖아. 졌어?", [FAKER, BLG])
    assert s.entity.display == "Faker" and s.polarity == "loss" and s.counterpart.display == "BLG"


def test_subject_topic_marker_wins_over_order():
    s = subject_of("BLG 상대로 T1은 왜 약해?", [BLG, T1])
    assert s.entity.display == "T1"


def test_why_upgrade():
    assert upgrade_intent("team_record", "why") == "matchup_pattern"
    assert upgrade_intent("team_form", "why", has_match_context=True) == "match_review"
    assert upgrade_intent("player_stat", "how") == "player_form"
    assert upgrade_intent("team_roster", "why") == "team_roster"


def test_registry_has_team_compare_and_new_intents():
    # L2 35종 vs L3 34종 문제 — team_compare 누락 해소 + 신규 matchup_pattern
    for i in ("team_compare", "matchup_pattern", "turning_point", "match_review"):
        assert i in INTENTS


def test_enrich_keeps_dropped_fields_and_page_context(q1):
    r = enrich(q1["raw_route"], q1["question"], has_match_context=True)
    assert r.intent == "match_review" and r.question_form == "why"
    assert r.verdict == "clear"                      # 지금은 소켓에서 버려지는 필드
    assert r.subject.entity.display == "T1" and r.subject.polarity == "loss"

    raw = {"path": "answer", "domain": "esports", "intent": "player_stat",
           "slots": {"entity_refs": [], "metrics": ["kill_participation"]}}
    ctx = {"page": {"type": "player", "entity_id": "98767991747728851", "display": "Faker", "scope_hint": "season"}}
    r2 = enrich(raw, "킬 관여율 얼마야?", page_context=ctx)
    assert r2.entity_refs[0].display == "Faker" and r2.scope == "season"
