"""층 사이를 오가는 데이터 계약 (L2 → L3 → L4 → 웹).

계약 원본은 contracts/*.schema.json. 이 파일은 같은 모양을 파이썬 dataclass로 옮긴 것이다.
필드를 바꿀 때는 schema.json · 이 파일 · docs/ 해당 층 문서를 함께 고친다 (docs/decisions.md D-004).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal, Optional

CONTRACT_VERSION = "ask-v2.0"
MUSE_CUE_VERSION = "muse-cue-v1.0"
MUSE_MESSAGE_VERSION = "muse-v1.0"

QuestionForm = Literal["what", "why", "how", "when", "compare"]
Polarity = Literal["win", "loss", "neutral"]
Turning = Literal["teamfight", "objective", "none", "unknown"]
Phase = Literal["early", "mid", "late", "unknown"]
Trend = Literal["sudden_drop", "sudden_rise", "slow_drop", "slow_rise", "even", "unknown"]
MuseKind = Literal["reply", "echo", "proactive"]
MuseSurface = Literal["extension", "web_sd"]
BlockName = Literal["lead", "history", "facts", "lens", "evidence", "next"]


@dataclass
class EntityRef:
    name: str            # 질문에 쓰인 원문 표기 (예: 폐이커) — 조회는 id로
    type: str            # player | team | champion | position | league | tournament
    id: str
    display: Optional[str] = None  # 화면 표기 (예: Faker, T1). L2 사전에서 채움


@dataclass
class Subject:
    """질문의 주어 — 답변 결론은 이 엔티티 관점으로 쓴다 (가드레일 G1)."""
    entity: Optional[EntityRef]
    polarity: Polarity = "neutral"       # 질문이 전제한 결과: "졌어?" → loss
    counterpart: Optional[EntityRef] = None  # 상대 (있으면)


@dataclass
class RouteResult:
    """L2 → L3. 현행 /route 응답 + v2 필드.

    현행 필드는 그대로 둔다. verdict · null_reason · unresolved 는 지금 소켓·백엔드에서
    버려지는데(L3 프로세스 문서), v2부터는 끝까지 전달한다.
    """
    path: str                                # answer | llm | clarify
    domain: Optional[str]
    topic: Optional[str]
    intent: Optional[str]
    verdict: Optional[str] = None            # clear | fuzzy | unclear
    null_reason: Optional[str] = None
    entity_refs: list[EntityRef] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)
    metrics: list[str] = field(default_factory=list)
    scope: Optional[str] = None
    conf: Optional[float] = None
    # ---- v2 ----
    question_form: QuestionForm = "what"
    subject: Optional[Subject] = None
    intent_registry_version: str = ""
    surface: str = "web"


@dataclass
class LensValue:
    label: str
    value: float
    unit: Optional[str] = None
    note: Optional[str] = None


@dataclass
class Lens:
    """RORR 분석 블록 하나 (목업의 탭 하나)."""
    lens_id: str                     # winprob_curve | objective_swing | death_breakdown | lwrc_by_game ...
    title: str
    metric: str                      # glossary.METRICS 키 — 라벨·기준이 반드시 붙는다 (G4)
    series: list[LensValue] = field(default_factory=list)
    markers: list[dict[str, Any]] = field(default_factory=list)  # 변곡점 등
    insight: Optional[str] = None    # L4가 채우는 한 줄 (숫자는 series 값만)
    free_drilldown: bool = True      # 답변 안 탭은 Energy 0
    sources: list[str] = field(default_factory=list)


@dataclass
class NarrativeRef:
    fact_id: str
    text: str                        # 서사 카드에 등록된 문장 (LLM이 새로 쓰지 않음)
    basis: str                       # 기준 (예: "Worlds 녹아웃 시리즈, 2023~")
    source: str


@dataclass
class MuseCue:
    """L3 → 페르소나 경로. 서하 대사의 재료 — 방향과 종류만, 숫자형 필드 없음 (D-026).

    유저별 정보(친밀도 · Fan심 · 감정)는 여기에 없다. 페르소나 경로가 붙인다.
    """
    outcome: str
    polarity: Polarity = "neutral"
    question_form: QuestionForm = "what"
    subject: Optional[dict[str, str]] = None      # {id, display} — id 는 Fan심 대조용
    counterpart: Optional[dict[str, str]] = None
    turning: Turning = "unknown"                  # 어디서 갈렸나
    phase: Phase = "unknown"                      # 언제 갈렸나 (초 · 중 · 후반)
    trend: Trend = "unknown"                      # 주어 관점 흐름
    has_narrative: bool = False
    has_report: bool = False                      # 가리킬 웹 리포트가 있는가
    ref: Optional[str] = None                     # MuseMessage.cue_ref 가 가리키는 값
    version: str = MUSE_CUE_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MuseMessage:
    """페르소나 경로 → 확장 · 웹 SD 서하. 웹 리포트 봉투와 따로 온다 (D-025 · D-026)."""
    kind: MuseKind                                # reply | echo(웹 검색 뒤 첨언) | proactive(선발화)
    surface: MuseSurface
    text: str                                     # 숫자 · 지표명 · 충전 권유 금지
    expression: Optional[dict[str, Any]] = None   # {code, variant, intensity} — Affect Engine
    action: Optional[dict[str, Any]] = None       # {code, variant}
    cue_ref: Optional[str] = None                 # echo 는 필수
    tier: str = "T1"                              # T1 템플릿 | T2 페르소나 LLM
    version: str = MUSE_MESSAGE_VERSION

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class L3Bundle:
    """L3 → L4. 조회 결과 + 분석 + 서사 + 출처 + 원가."""
    route: RouteResult
    facts_kind: Optional[str]                     # 기존 VizEnvelope kind
    facts_rows: list[dict[str, Any]] = field(default_factory=list)
    facts_meta: dict[str, Any] = field(default_factory=dict)  # 경기 단위 사실 (스코어·시간 등)
    lenses: list[Lens] = field(default_factory=list)
    narratives: list[NarrativeRef] = field(default_factory=list)
    teams: dict[str, str] = field(default_factory=dict)  # side("100"/"200") → 팀 코드
    data_scope: str = "2026"                      # 화면에 "2026 데이터 기준"으로 표기
    sources: list[str] = field(default_factory=list)
    cost_krw: float = 0.0
    outcome: str = "answered"                     # energy.OUTCOMES
    muse_cue: Optional[MuseCue] = None            # 서하용 재료 — 웹 리포트 봉투로는 안 간다


@dataclass
class AnswerEnvelope:
    """L4 → 웹 리포트 봉투. 서하 대사는 담지 않는다 — 별도 Muse 메시지 (D-025 · D-026)."""
    version: str
    lead: dict[str, str]                          # {text, sub}
    history: list[dict[str, str]]                 # Ⓗ 역대 맥락 (서사 카드 기반)
    facts: Optional[dict[str, Any]]               # ② 사실 카드 (기존 kind)
    lenses: list[dict[str, Any]]                  # ③ RORR 분석
    evidence: list[str]                           # ④ 근거 칩
    next: list[dict[str, Any]]                    # ④ 후속 질문 {text, energy}
    energy: dict[str, Any]                        # {cost, charged, reason}
    data_scope_label: str = ""
    violations: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
