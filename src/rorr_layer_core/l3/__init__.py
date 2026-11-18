"""L3 — 컨텍스트 조립 층. 기존 쿼리 생성 뒤에 RORR 분석·서사·출처·outcome을 붙인다."""
from .bundle import assemble, lens_from_report
from .lenses import LENSES, plan_lenses
from .match_report import build_match_report, death_breakdown, top_swings, turning_points
from .narrative import NarrativeFact, NarrativeStore

__all__ = ["assemble", "lens_from_report", "LENSES", "plan_lenses", "build_match_report",
           "death_breakdown", "top_swings", "turning_points", "NarrativeFact", "NarrativeStore"]
