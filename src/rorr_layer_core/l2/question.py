"""L2 v2 추가 판정 — 질문 형태(question_form)와 주어·극성(subject).

둘 다 규칙 기반이다. 티어·경로 판정에 LLM을 쓰지 않는다는 기존 원칙과 같고,
Jev 호출 수(현재 메시지당 1.91회)를 늘리지 않는다.

왜 필요한가 (faker 질의 로그 2026-11-09)
- "faker BLG 경기는? 오늘 있었잖아. 졌어?" → 답변 "네, BLG는 이겼어요"
  질문의 주어(Faker)와 전제(졌다)를 잡지 못해 상대 팀 관점으로 답했다.
- "이번 BLG 경기에서 어떤 점이 아쉬웠어?" → 이벤트 연대기만 나열
  "왜/아쉬운 점"을 해설형 질문으로 인식하지 못했다.
"""
from __future__ import annotations

import re

from ..contracts import EntityRef, Subject

_WHY = re.compile(r"왜|어째서|이유|원인|아쉬|뭐가 문제|무엇이 문제|어디서 (갈|넘어|밀)|why", re.I)
_WHEN = re.compile(r"언제|몇 시|며칠|when", re.I)
_COMPARE = re.compile(r"\bvs\b|비교|누가 더|어느 쪽|차이", re.I)
_HOW = re.compile(r"어때|어땠|폼|컨디션|잘해|못해|how", re.I)

_LOSS = re.compile(r"졌|지냐|지나|졌냐|패배|패했|탈락|떨어졌|무너")
_WIN = re.compile(r"이겼|이기냐|이기나|승리|우승|올라갔|진출")


def question_form(text: str) -> str:
    """what | why | how | when | compare. 우선순위: why > compare > when > how > what."""
    if _WHY.search(text):
        return "why"
    if _COMPARE.search(text):
        return "compare"
    if _WHEN.search(text):
        return "when"
    if _HOW.search(text):
        return "how"
    return "what"


def polarity(text: str) -> str:
    if _LOSS.search(text):
        return "loss"
    if _WIN.search(text):
        return "win"
    return "neutral"


_SUBJECT_TYPES = ("player", "team")


def _position(text: str, ref: EntityRef) -> int:
    for token in filter(None, (ref.name, ref.display)):
        i = text.lower().find(token.lower())
        if i >= 0:
            return i
    return 10**6


def subject_of(text: str, refs: list[EntityRef]) -> Subject:
    """질문의 주어를 고른다.

    규칙
    1. 선수·팀 엔티티만 후보.
    2. 주격·주제 조사(은/는/이/가)가 바로 붙은 엔티티가 있으면 그게 주어.
    3. 없으면 문장에서 먼저 나온 엔티티.
    4. 나머지 첫 후보를 상대(counterpart)로 둔다.
    """
    cands = [r for r in refs if r.type in _SUBJECT_TYPES]
    if not cands:
        return Subject(entity=None, polarity=polarity(text))  # type: ignore[arg-type]

    def marked(ref: EntityRef) -> bool:
        for token in filter(None, (ref.name, ref.display)):
            if re.search(re.escape(token) + r"\s?(은|는|이|가|도)(\s|$)", text, re.I):
                return True
        return False

    ordered = sorted(cands, key=lambda r: _position(text, r))
    marked_refs = [r for r in ordered if marked(r)]
    subj = marked_refs[0] if marked_refs else ordered[0]
    others = [r for r in ordered if r is not subj]
    return Subject(entity=subj, polarity=polarity(text), counterpart=others[0] if others else None)  # type: ignore[arg-type]
