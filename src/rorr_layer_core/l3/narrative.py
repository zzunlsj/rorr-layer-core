"""역대 서사 카드 (narrative_fact) — 2026 밖의 맥락을 보충한다 (D-007).

지금 데이터는 2026 시즌뿐이라 "T1은 BLG 상대로 왜 약해?"가 "1승 4패"로 끝난다.
하지만 T1은 몇 년 동안 Worlds에서 LPL 팀에 진 적이 없었고, 이번 4강이 첫 패배다.
이런 맥락은 지금은 사람이 검증해 등록하고(서사 카드), 나중에 역대 데이터를 적재하면
같은 테이블에 auto_derived=True 로 자동 도출 카드가 들어온다 (P3).

원칙
- LLM은 카드 문장을 고르고 다듬기만 한다. 기록을 만들지 않는다 (가드레일 G9).
- status == verified 이고 유효 기간 안의 카드만 쓴다.
- 기록이 깨지면 valid_to 를 닫고 새 카드를 등록한다.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Iterable, Optional

from ..contracts import NarrativeRef


@dataclass
class NarrativeFact:
    fact_id: str
    entity_a: str                  # team/player id
    text: str
    basis: str                     # 기준: "Worlds 녹아웃 시리즈, 2023~" 처럼 범위를 반드시 적는다
    source: str
    kind: str = "streak_break"     # streak_break | rivalry | league_rivalry | career | rematch
    entity_b: Optional[str] = None # 상대 id 또는 리그 코드("LPL")
    scope: Optional[str] = None    # worlds | msi | lck ...
    status: str = "draft"          # draft | verified | retired
    verified_by: Optional[str] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    auto_derived: bool = False
    tags: list[str] = field(default_factory=list)


class NarrativeStore:
    """메모리 구현. 운영은 Postgres narrative_fact 테이블 (sql/002_narrative_fact.sql)."""

    def __init__(self, facts: Iterable[NarrativeFact] = ()):
        self._facts = list(facts)

    def add(self, fact: NarrativeFact) -> None:
        self._facts.append(fact)

    def match(self, entity_ids: set[str], leagues: set[str] | None = None, scope: str | None = None,
              today: date | None = None, limit: int = 1) -> list[NarrativeRef]:
        """질문 엔티티와 맞는 카드. 두 엔티티가 모두 맞는 카드를 먼저 낸다."""
        today = today or date.today()
        leagues = leagues or set()
        scored = []
        for f in self._facts:
            if f.status != "verified":
                continue
            if f.valid_from and f.valid_from > today:
                continue
            if f.valid_to and f.valid_to < today:
                continue
            if f.entity_a not in entity_ids:
                continue
            score = 1
            if f.entity_b and (f.entity_b in entity_ids or f.entity_b in leagues):
                score += 2
            elif f.entity_b:
                continue  # 상대가 지정된 카드인데 질문 상대와 다르면 쓰지 않는다
            if scope and f.scope == scope:
                score += 1
            scored.append((score, f))
        scored.sort(key=lambda x: -x[0])
        return [NarrativeRef(fact_id=f.fact_id, text=f.text, basis=f.basis, source=f.source)
                for _, f in scored[:limit]]
