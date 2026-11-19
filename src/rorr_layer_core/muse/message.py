"""Muse 메시지 출력 검사 — 웹 SD 첨언과 Extension 대사에 같은 규칙을 건다 (D-026).

M1 | 서하 대사에 숫자 · 지표명 (= G8)            | 3채널 UX 원칙
M2 | 충전 · Boost 권유                            | no_dependency
M3 | echo(웹 첨언)인데 cue_ref 가 없음            | 어느 검색에 붙는 말인지 웹이 알 수 없다
M4 | 웹 SD 서하가 echo 가 아닌 말을 함            | 웹의 서하는 검색 뒤 첨언만 한다 (D-026)

엔티티 표기에 든 숫자("T1")는 수치가 아니므로 검사 전에 지운다.
"""
from __future__ import annotations

import re
from typing import Optional

from ..contracts import MuseCue, MuseMessage
from ..l4.glossary import METRICS
from ..l4.guardrails import Violation, check_muse

_DEPENDENCY = re.compile(r"충전|결제|부스트|boost|에너지\s*(사|구매)", re.IGNORECASE)


def check_message(msg: MuseMessage, cue: Optional[MuseCue] = None,
                  entity_names: tuple[str, ...] = ()) -> list[Violation]:
    names = list(entity_names)
    if cue:
        names += [e["display"] for e in (cue.subject, cue.counterpart) if e]
    text = msg.text
    for n in sorted(names, key=len, reverse=True):
        text = text.replace(n, "")

    out = [Violation("M1", "muse", v.message) for v in check_muse(text, [m[0] for m in METRICS.values()])]
    if _DEPENDENCY.search(msg.text):
        out.append(Violation("M2", "muse", "충전 · Boost 권유"))
    if msg.kind == "echo" and not msg.cue_ref:
        out.append(Violation("M3", "muse", "echo 인데 cue_ref 없음"))
    if msg.surface == "web_sd" and msg.kind != "echo":
        out.append(Violation("M4", "muse", "웹 SD 서하는 검색 뒤 첨언(echo)만 한다"))
    return out
