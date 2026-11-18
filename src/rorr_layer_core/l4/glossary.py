"""표기 사전 — raw 값이 화면에 그대로 나가지 않게 한다 (P0 가드레일).

faker 질의 로그(2026-11-09)에서 나온 문제
- "1395635초 무렵"     → 게임 시간 ms 를 초로 착각. mm:ss 로 바꾼다.
- "100 측 / 200 측"    → side 를 팀 코드로 바꾼다.
- "화학 공학 용"       → dragon_type 한글 표기 사전.
- "총 39 (분당 1.21, 플러스 0.3)" → 지표 이름·기준 없이 숫자만. METRICS 라벨을 반드시 붙인다.
"""
from __future__ import annotations

import re

DRAGON_KO = {
    "fire": "화염 드래곤", "infernal": "화염 드래곤",
    "earth": "대지 드래곤", "mountain": "대지 드래곤",
    "air": "바람 드래곤", "cloud": "바람 드래곤",
    "water": "바다 드래곤", "ocean": "바다 드래곤",   # raw 값은 'water' (LoL 데이터 레이어 확인)
    "hextech": "마법공학 드래곤", "chemtech": "화학공학 드래곤",
    "elder": "장로 드래곤",
}

# metric 키 → (화면 이름, 기준 설명 or None, 단위)
METRICS: dict[str, tuple[str, str | None, str]] = {
    "lwrc_plus": ("LwRC+", "같은 대회·포지션 평균 = 100", ""),
    "lwrc_component": ("LwRC 구성 (획득 C · 차단 D · 위험 Risk)", "게임당 팀 기대 골드", "골드"),
    "teamfight_win_prob": ("한타 승률", "지금 5:5로 붙으면 이길 확률 · 5~95%로 표시", "%"),
    "objective_impact": ("오브젝트 영향력", "획득 후 60초 골드 격차 × 오브젝트 중요도", "골드"),
    "damage_share": ("받은 피해 비중", "데스 직전 가해자별 피해 합 = 100%", "%"),
    "gold_diff": ("골드 차", "질문한 팀 기준", "골드"),
    "rate_pct": ("획득률", None, "%"),
    "win_rate_pct": ("승률", None, "%"),
    "kda": ("KDA", "(킬+어시스트)/데스", ""),
}


def metric_label(key: str) -> tuple[str, str | None]:
    name, basis, _ = METRICS[key]
    return name, basis


def fmt_game_time(ms: int | float) -> str:
    """게임 시간 ms → mm:ss. (game_combat_event.game_time 은 ms)"""
    sec = int(ms) // 1000
    return f"{sec // 60}:{sec % 60:02d}"


def side_to_team(side: int | str, teams: dict[str, str]) -> str:
    return teams.get(str(side), "블루" if str(side) == "100" else "레드")


_RAW_TIME = re.compile(r"(\d{5,})\s*초")
_RAW_SIDE = re.compile(r"\b(100|200)\s*(측|진영|사이드|팀)")
_DRAGON_EN = re.compile(r"\b(" + "|".join(DRAGON_KO) + r")\s*(dragon|드래곤|용)?", re.I)
_BAD_KO_DRAGON = {"화학 공학 용": "화학공학 드래곤", "마법 공학 용": "마법공학 드래곤"}


def normalize_text(text: str, teams: dict[str, str]) -> str:
    """LLM 문장에 섞인 raw 표기를 사람 표기로 바꾼다. 의미가 바뀌는 수정은 하지 않는다."""
    text = _RAW_TIME.sub(lambda m: fmt_game_time(int(m.group(1))), text)
    text = _RAW_SIDE.sub(lambda m: side_to_team(m.group(1), teams), text)
    for bad, good in _BAD_KO_DRAGON.items():
        text = text.replace(bad, good)
    text = _DRAGON_EN.sub(lambda m: DRAGON_KO[m.group(1).lower()], text)
    return text
