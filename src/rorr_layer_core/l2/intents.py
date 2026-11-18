"""L2 intent 레지스트리 — L2와 L3가 같은 버전을 본다 (D-002).

현재 문제(L3 프로세스 문서): L2 35종 vs L3 매핑 34종(team_compare 없음).
v2는 이 레지스트리 하나를 기준으로 두 층이 같이 갱신한다.

category
- fact      : 누구나 가진 데이터로 답하는 질문 (일정·로스터·전적·스탯)
- interpret : 해설 — RORR 분석(lens)이 핵심인 질문
- live      : 진행 중 경기
- reference : 사양·용어·규정
"""
from __future__ import annotations

INTENT_REGISTRY_VERSION = "2026.11-v2"

# intent → (topic, category, 기본 lens 목록)
INTENTS: dict[str, tuple[str, str, tuple[str, ...]]] = {
    # 일정
    "next_match": ("schedule", "fact", ()),
    "match_fixture": ("schedule", "fact", ()),
    "season_calendar": ("schedule", "fact", ()),
    # 선수
    "player_profile": ("player", "fact", ()),
    "player_stat": ("player", "fact", ("lwrc_summary",)),
    "player_form": ("player", "interpret", ("lwrc_by_game", "lwrc_cdr")),
    "player_champion": ("player", "fact", ()),
    "player_compare": ("player", "interpret", ("lwrc_cdr",)),
    # 팀
    "team_roster": ("team", "fact", ()),
    "team_record": ("team", "fact", ()),
    "team_standing": ("team", "fact", ()),
    "team_form": ("team", "fact", ()),
    "team_stat": ("team", "fact", ()),
    "team_champions": ("team", "fact", ()),
    "team_compare": ("team", "interpret", ("gold_diff_by_minute",)),  # L3 매핑 누락분 (D-002)
    # 해석
    "match_review": ("analysis", "interpret", ("winprob_curve", "objective_swing", "death_breakdown")),
    "player_review": ("analysis", "interpret", ("lwrc_by_game", "lwrc_cdr", "death_breakdown")),
    "teamfight_analysis": ("analysis", "interpret", ("winprob_curve", "death_breakdown")),
    "turning_point": ("analysis", "interpret", ("winprob_curve", "objective_swing")),
    "matchup_pattern": ("analysis", "interpret", ("gold_diff_by_minute", "first_objective_rate", "role_matchup")),  # 신규
    # 사양
    "champion_info": ("reference", "reference", ()),
    "item_info": ("reference", "reference", ()),
    "rune_info": ("reference", "reference", ()),
    "build_guide": ("reference", "reference", ()),
    "term_info": ("reference", "reference", ()),
    "meta_info": ("reference", "reference", ()),
    "patch_info": ("reference", "reference", ()),
    "rules_info": ("reference", "reference", ()),
    # 실시간
    "game_state": ("ingame", "live", ()),
    "objective_status": ("ingame", "live", ()),
    "objective_priority": ("ingame", "live", ()),
    "vision_control": ("ingame", "live", ()),
    "lane_matchup": ("ingame", "live", ()),
    "jungle_pathing": ("ingame", "live", ()),
    "draft_evaluation": ("ingame", "live", ()),
    "win_prediction": ("ingame", "live", ("winprob_curve",)),
    "comeback_odds": ("ingame", "live", ("winprob_curve",)),
}

# "왜"로 물었을 때 사실형 intent를 해설형으로 올린다 (D-003).
# 예) "T1은 BLG 상대로 왜 약해?" — Jev는 team_record로 보기 쉽지만 원하는 건 패턴 해설.
WHY_UPGRADE: dict[str, str] = {
    "team_record": "matchup_pattern",
    "team_form": "matchup_pattern",
    "team_stat": "matchup_pattern",
    "team_compare": "matchup_pattern",
    "player_stat": "player_review",
    "player_form": "player_review",
    "player_champion": "player_review",
    "game_state": "turning_point",
}
HOW_UPGRADE: dict[str, str] = {   # "폼 어때?" 같은 평가형
    "player_stat": "player_form",
    "team_stat": "team_form",
}


def topic_of(intent: str | None) -> str | None:
    return INTENTS[intent][0] if intent in INTENTS else None


def category_of(intent: str | None) -> str | None:
    return INTENTS[intent][1] if intent in INTENTS else None


def default_lenses(intent: str | None) -> tuple[str, ...]:
    return INTENTS[intent][2] if intent in INTENTS else ()


def is_interpretive(intent: str | None) -> bool:
    return category_of(intent) == "interpret"


def upgrade_intent(intent: str | None, question_form: str, has_match_context: bool = False) -> str | None:
    """질문 형태에 따라 intent를 해설형으로 올린다. 모르면 그대로 둔다."""
    if intent is None:
        return None
    if question_form == "why":
        if intent in ("match_result", "team_form") and has_match_context:
            return "match_review"
        return WHY_UPGRADE.get(intent, intent)
    if question_form == "how":
        return HOW_UPGRADE.get(intent, intent)
    return intent
