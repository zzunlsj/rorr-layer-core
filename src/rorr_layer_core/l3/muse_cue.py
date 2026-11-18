"""MuseCue — L3 가 서하(페르소나 경로)에게 넘기는 숫자 없는 재료 (D-026).

리포트를 만들 때 이미 계산한 lens 에서 **방향과 종류만** 뽑는다. 추가 조회 · LLM 호출이 없다.
값(승률 · 골드 · 시각)을 싣지 않으므로 서하 대사에 숫자가 들어갈 길이 구조적으로 없다.
유저별 정보가 없어서 리포트 캐시와 같은 키로 나눠 쓸 수 있다.

판정 규칙 (v1)
- turning : 한타 승률 변곡점이 있으면 teamfight / 없고 오브젝트 스윙이 있으면 objective /
            한타 승률 흐름은 있는데 둘 다 없으면 none / 재료가 없으면 unknown
- phase   : 변곡점 시각이 14분 전 early · 25분 전 mid · 그 뒤 late
- trend   : 변곡점이 있으면 sudden_drop / sudden_rise, 없으면 처음과 끝의 차이로 slow_* / even
"""
from __future__ import annotations

from typing import Optional

from ..contracts import EntityRef, Lens, MuseCue, RouteResult

EARLY_END_SEC = 14 * 60
MID_END_SEC = 25 * 60
SLOW_CHANGE = 15.0     # 변곡점 없이 처음 ↔ 끝 한타 승률이 이만큼(%p) 움직이면 slow_*


def _entity(e: Optional[EntityRef]) -> Optional[dict[str, str]]:
    return {"id": e.id, "display": e.display or e.name} if e else None


def _lens(lenses: list[Lens], lens_id: str) -> Optional[Lens]:
    return next((l for l in lenses if l.lens_id == lens_id), None)


def build_muse_cue(route: RouteResult, lenses: list[Lens], outcome: str, has_narrative: bool = False,
                   ref: Optional[str] = None) -> MuseCue:
    subj = route.subject
    cue = MuseCue(outcome=outcome, polarity=subj.polarity if subj else "neutral",
                  question_form=route.question_form,
                  subject=_entity(subj.entity) if subj else None,
                  counterpart=_entity(subj.counterpart) if subj else None,
                  has_narrative=has_narrative, has_report=outcome == "answered" and bool(lenses), ref=ref)
    if outcome != "answered":
        return cue

    curve = _lens(lenses, "winprob_curve")
    swing = _lens(lenses, "objective_swing")
    # 변곡점이 여럿이면 가장 크게 움직인 것 하나로 말한다
    marker = max(curve.markers, key=lambda m: abs(m["before"] - m["after"])) if curve and curve.markers else None

    if marker:
        cue.turning = "teamfight"
        cue.phase = "early" if marker["t"] < EARLY_END_SEC else "mid" if marker["t"] < MID_END_SEC else "late"
        cue.trend = "sudden_drop" if marker["after"] < marker["before"] else "sudden_rise"
    elif swing and swing.series:
        cue.turning = "objective"
    elif curve:
        cue.turning = "none"

    if curve and curve.series and not marker:
        change = curve.series[-1].value - curve.series[0].value
        cue.trend = "slow_drop" if change <= -SLOW_CHANGE else "slow_rise" if change >= SLOW_CHANGE else "even"
    return cue
