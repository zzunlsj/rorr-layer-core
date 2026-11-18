"""현행 L2 /route 응답(JSON) → RouteResult v2.

현행 라우터(Jev 판정, rorr-user-intent-router — D-020)를 고치지 않고 뒤에 붙이는 후처리기다.
라우터 코드에 직접 넣을 때도 이 함수 순서를 그대로 따른다.

순서
1. 현행 필드 보존 (verdict · null_reason · unresolved 포함 — 지금은 null_reason 은 소켓, 나머지는 백엔드에서 끊김)
2. 웹 페이지 맥락을 슬롯 기본값으로 (덮어쓰기 아님) — 대화 레이어 구조 문서 §2
3. question_form · subject 판정 (규칙)
4. "왜/어때" 질문이면 intent를 해설형으로 올림
"""
from __future__ import annotations

from typing import Any, Optional

from ..contracts import EntityRef, RouteResult
from .intents import INTENT_REGISTRY_VERSION, topic_of, upgrade_intent
from .question import question_form, subject_of


def _refs(raw: list[dict[str, Any]]) -> list[EntityRef]:
    return [EntityRef(name=r["name"], type=r["type"], id=str(r["id"]), display=r.get("display")) for r in raw]


def enrich(route: dict[str, Any], text: str, page_context: Optional[dict[str, Any]] = None,
           has_match_context: bool = False, surface: str = "web") -> RouteResult:
    slots = route.get("slots") or {}
    refs = _refs(slots.get("entity_refs", []))

    # 2. 페이지 맥락 — 주어 없는 질문("킬 관여율 얼마야?")을 보고 있는 선수로 채운다
    if page_context and not any(r.type in ("player", "team") for r in refs):
        page = page_context.get("page") or {}
        if page.get("type") in ("player", "team") and page.get("entity_id"):
            refs.append(EntityRef(name=page.get("display", ""), type=page["type"], id=str(page["entity_id"]),
                                  display=page.get("display")))

    form = question_form(text)
    intent = upgrade_intent(route.get("intent"), form, has_match_context=has_match_context)

    scope = route.get("scope")
    if page_context and (page_context.get("page") or {}).get("scope_hint"):
        scope = scope or page_context["page"]["scope_hint"]  # 맥락 > 텍스트 > DB (D-005)

    return RouteResult(
        path=route.get("path", "answer"),
        domain=route.get("domain"),
        topic=topic_of(intent) or route.get("topic"),
        intent=intent,
        verdict=route.get("verdict"),
        null_reason=route.get("null_reason"),
        entity_refs=refs,
        unresolved=list(slots.get("unresolved", [])),
        metrics=list(slots.get("metrics", [])),
        scope=scope,
        conf=route.get("conf"),
        question_form=form,  # type: ignore[arg-type]
        subject=subject_of(text, refs),
        intent_registry_version=INTENT_REGISTRY_VERSION,
        surface=surface,
    )
