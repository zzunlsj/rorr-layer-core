"""L4 가드레일 — LLM 초안을 웹으로 보내기 전에 코드가 검사한다.

코드 | 무엇을 막나 | 근거
G1 | 결론이 질문한 주어 관점이 아님               | faker 로그 Q2 ("졌어?" → "BLG는 이겼어요")
G2 | 게임 시간 raw(ms를 초로) 노출                | faker 로그 Q3 ("1395635초")
G3 | 진영 번호(100/200) 노출                      | faker 로그 Q3 ("100 측")
G4 | 라벨·기준 없는 지표                          | faker 로그 Q4 ("총 39, 플러스 0.3")
G5 | 문장 속 개수와 표 행 수 불일치               | faker 로그 Q1 ("최근 5경기" + 6행)
G6 | 사실 표 행 과다 (raw 덤프)                   | faker 로그 Q3 (이벤트 66행)
G7 | 한국어 문구에 이질 문자(한자·가나·키릴)       | L4 프롬프트 초안 §5-5
G8 | 서하 대사에 숫자·지표명                      | 3채널 UX 원칙
G9 | 서사 문장이 등록된 카드에서 오지 않음        | 방향성 4-1
G10| 유료 답변인데 RORR 분석이 없음 (경고)        | 방향성 §2 (120원의 값)

severity
- block : 해당 블록을 버리거나 템플릿으로 교체 (envelope.py)
- warn  : 기록만 하고 내보냄 (대시보드 집계용)
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from ..contracts import L3Bundle, Subject
from .glossary import METRICS

_FOREIGN = re.compile(r"[぀-ヿ一-鿿Ѐ-ӿ]")
_RAW_TIME = re.compile(r"\d{5,}\s*초")
_RAW_SIDE = re.compile(r"\b(100|200)\s*(측|진영|사이드)")
_DIGIT = re.compile(r"\d")
_COUNT = re.compile(r"(최근|지난)\s*(\d+)\s*(경기|게임|세트)")
_WIN_WORDS = ("이겼", "승리", "꺾었")
MAX_FACT_ROWS = 10


@dataclass
class Violation:
    code: str
    block: str
    message: str
    severity: str = "block"


def _names(ref) -> list[str]:
    return [n for n in (getattr(ref, "display", None), getattr(ref, "name", None)) if n]


def check_subject(lead: str, subject: Subject | None) -> list[Violation]:
    if not subject or not subject.entity:
        return []
    out = []
    if not any(n.lower() in lead.lower() for n in _names(subject.entity)):
        out.append(Violation("G1", "lead", f"결론에 질문 주어({_names(subject.entity)[0]})가 없음"))
    if subject.polarity == "loss" and subject.counterpart:
        first = re.split(r"[.?!]", lead, maxsplit=1)[0]
        subj_pos = min((first.find(n) for n in _names(subject.entity) if n in first), default=-1)
        for n in _names(subject.counterpart):
            cp_pos = first.find(n)
            if cp_pos >= 0 and (subj_pos < 0 or cp_pos < subj_pos) and any(w in first for w in _WIN_WORDS):
                out.append(Violation("G1", "lead", f"패배를 물었는데 상대({n}) 승리로 답을 시작함"))
                break
    return out


def check_text(block: str, text: str) -> list[Violation]:
    out = []
    if _RAW_TIME.search(text):
        out.append(Violation("G2", block, "게임 시간 raw 값 노출"))
    if _RAW_SIDE.search(text):
        out.append(Violation("G3", block, "진영 번호 노출"))
    if _FOREIGN.search(text):
        out.append(Violation("G7", block, "이질 문자 포함"))
    return out


def check_lenses(lenses: list[dict[str, Any]]) -> list[Violation]:
    out = []
    for lens in lenses:
        m = lens.get("metric")
        if m not in METRICS:
            out.append(Violation("G4", "lens", f"등록되지 않은 지표: {m}"))
            continue
        name, basis, _ = METRICS[m]
        if not lens.get("metric_label") or (basis and not lens.get("metric_basis")):
            out.append(Violation("G4", "lens", f"{name}에 라벨/기준이 없음"))
    return out


def check_counts(texts: list[str], n_rows: int) -> list[Violation]:
    out = []
    for t in texts:
        for m in _COUNT.finditer(t):
            if n_rows and int(m.group(2)) != n_rows:
                out.append(Violation("G5", "lead", f"문장 '{m.group(0)}'과 표 {n_rows}행이 다름"))
    return out


def check_facts(rows: list[Any]) -> list[Violation]:
    if len(rows) > MAX_FACT_ROWS:
        return [Violation("G6", "facts", f"사실 표 {len(rows)}행 — 상위 {MAX_FACT_ROWS}행만 보이고 나머지는 접기",
                          severity="warn")]
    return []


def check_muse(line: str, metric_names: list[str]) -> list[Violation]:
    """G8 — 서하 대사 규칙. 웹 리포트 봉투에는 서하 대사가 없으므로 run_all 에서 부르지 않는다.
    Muse 메시지를 만드는 페르소나 경로(웹 SD 첨언 · 확장 대사)의 출력 검사에 쓴다 (D-026)."""
    if _DIGIT.search(line) or any(n in line for n in metric_names):
        return [Violation("G8", "muse", "서하 대사에 숫자·지표명")]
    return []


def check_history(history: list[dict[str, str]], bundle: L3Bundle) -> list[Violation]:
    allowed = {n.fact_id for n in bundle.narratives}
    return [Violation("G9", "history", "등록되지 않은 서사 문장")
            for h in history if h.get("fact_id") not in allowed]


def check_paid_value(lenses: list[Any], energy_cost: int) -> list[Violation]:
    if energy_cost > 0 and not lenses:
        return [Violation("G10", "lens", "유료 답변인데 RORR 분석이 없음", severity="warn")]
    return []


def run_all(env: dict[str, Any], bundle: L3Bundle) -> list[Violation]:
    v: list[Violation] = []
    lead = env["lead"]["text"]
    v += check_subject(lead, bundle.route.subject)
    for block, text in (("lead", lead), ("lead", env["lead"].get("sub", ""))):
        v += check_text(block, text)
    for lens in env["lenses"]:
        v += check_text("lens", lens.get("insight") or "")
    v += check_lenses(env["lenses"])
    v += check_counts([lead, env["lead"].get("sub", "")], len(bundle.facts_rows))
    v += check_facts(bundle.facts_rows)
    v += check_history(env.get("history", []), bundle)
    v += check_paid_value(env["lenses"], env["energy"]["cost"])
    return v
