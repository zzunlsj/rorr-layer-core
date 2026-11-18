"""L4 — 생성·표현 층. LLM은 문장만, 숫자·표·서사·Energy는 코드가."""
from .envelope import build
from .glossary import DRAGON_KO, METRICS, fmt_game_time, normalize_text
from .guardrails import run_all

__all__ = ["build", "DRAGON_KO", "METRICS", "fmt_game_time", "normalize_text", "run_all"]
