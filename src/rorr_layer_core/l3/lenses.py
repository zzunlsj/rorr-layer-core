"""RORR 분석(lens) 레지스트리 — intent별로 어떤 분석을 붙이고, 어디서 읽는지.

precomputed=True 인 lens는 경기 종료 배치(match_report_lens)에서 키로 읽는다 → L3 Sonnet 호출 없음.
precomputed=False 는 그래프·시계열 쿼리가 필요 — 첫 생성 후 쿼리 캐시(prepared_questions)에 올린다.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..l2.intents import default_lenses


@dataclass(frozen=True)
class LensSpec:
    lens_id: str
    title: str
    metric: str                 # l4.glossary.METRICS 키
    sources: tuple[str, ...]
    precomputed: bool
    needs_match: bool           # 특정 경기(game_id)가 정해져야 계산 가능한가
    available_from: str = "2026"  # 1Hz 라이브 데이터가 필요한 지표는 2026 이후만


LENSES: dict[str, LensSpec] = {
    "winprob_curve": LensSpec("winprob_curve", "한타 승률 흐름", "teamfight_win_prob",
                              ("win_probability_frame",), True, True),
    "objective_swing": LensSpec("objective_swing", "흐름을 바꾼 오브젝트", "objective_impact",
                                ("v_objective_swing", "obj_intensity_weight"), True, True),
    "death_breakdown": LensSpec("death_breakdown", "결정적 데스", "damage_share",
                                ("game_kill_damage", "v_kill_damage_breakdown"), True, True),
    "lwrc_by_game": LensSpec("lwrc_by_game", "경기별 LwRC+", "lwrc_plus",
                             ("lwrc players.json", "Neo4j CONTRIBUTED_IN"), True, False),
    "lwrc_cdr": LensSpec("lwrc_cdr", "어디서 벌었나 (C·D·Risk)", "lwrc_component",
                         ("lwrc players.json",), True, False),
    "lwrc_summary": LensSpec("lwrc_summary", "LwRC+ 요약", "lwrc_plus", ("lwrc players.json",), True, False),
    "gold_diff_by_minute": LensSpec("gold_diff_by_minute", "시간대별 골드 차", "gold_diff",
                                    ("cagg_team_state_30s",), False, False),
    "first_objective_rate": LensSpec("first_objective_rate", "첫 오브젝트 획득률", "rate_pct",
                                     ("Neo4j SECURED_OBJECTIVE",), False, False),
    "role_matchup": LensSpec("role_matchup", "라인 매치업", "win_rate_pct",
                             ("Neo4j ROLE_MATCHUP_VS",), False, False),
}


def plan_lenses(intent: str | None, has_game: bool) -> list[LensSpec]:
    """intent에 붙일 lens. 경기가 특정되지 않으면 경기 단위 lens는 뺀다."""
    out = []
    for lid in default_lenses(intent):
        spec = LENSES[lid]
        if spec.needs_match and not has_game:
            continue
        out.append(spec)
    return out


def estimated_cost_krw(specs: list[LensSpec], cache_hit: bool) -> float:
    """질문 1건 L3 원가 추정 — [L3] 쏘넷 5.5 비용 문서 기준값.

    배치 lens만 → 키 조회(₩0) / 쿼리 생성 필요 → 캐시 히트 ₩0, 한 번에 성공 ₩11, 평균 ₩41.
    """
    if all(s.precomputed for s in specs):
        return 0.0
    return 0.0 if cache_hit else 41.0
