"""L4 v2 프롬프트 — 기존 emit_viz(정형화기) 위에 '말'만 맡기는 도구 emit_answer.

역할 분리 (L4 프롬프트 테스트 초안 원칙 유지)
- Haiku : 결론 한 줄(lead) · 보충(sub) · lens별 한 줄 해석(insight) · 서하 반응 · 후속 질문 문구
- 코드  : 숫자·사실 표·lens 값·서사 문장·Energy (envelope.py)

기존 emit_viz 호출(사실 카드 kind)은 그대로 쓰고, 해설형 intent일 때만 emit_answer 를 한 번 더
부르거나(2회 호출), emit_viz 스키마에 아래 필드를 추가해 1회로 합친다 — D-008 에서 결정.
"""
from __future__ import annotations

SYSTEM_V2 = """너는 LoL e스포츠 답변의 '해설 문장'만 쓰는 작성기다.
입력: [질문] [질문 주어·극성] [사실 요약] [분석(lens) 값] [서사 카드].
반드시 emit_answer 도구로만 답한다.

[결론 lead]
- 질문한 주어의 관점으로 쓴다. 주어가 "T1"이고 "졌어?"라고 물었으면 "T1은 ~에서 졌어요/넘겨줬어요"로 시작한다.
  상대 팀을 주어로 시작하지 않는다.
- '왜'를 물었으면 결과가 아니라 갈린 지점(시점·장면)을 말한다.
- 숫자는 [분석] 또는 [사실 요약]에 있는 값만 쓴다. 계산·추정 금지.
- 지표를 말할 때는 이름을 함께 쓴다 (예: "LwRC+ 118"). 이름 없는 숫자 금지.

[lens insight]
- lens마다 한 줄. 그 lens 값으로 알 수 있는 '의미'를 쓴다. 값 나열 금지.

[muse — 서하 반응]
- 감정 한 줄. 숫자·지표명 금지. 충전·Boost 권유 금지.

[next — 후속 질문 3개]
- 같은 답 안에서 더 볼 수 있는 것 1개(무료 드릴다운), 새 질문 2개.

[금지]
- 게임 시간 원시값, 진영 번호(100/200), 영문 드래곤 타입을 문장에 쓰지 않는다.
- 서사 카드에 없는 역대 기록을 만들지 않는다.
- 한국어 문장에 한자·가나·키릴 문자를 쓰지 않는다.
"""

EMIT_ANSWER_TOOL = {
    "name": "emit_answer",
    "description": "해설형 답변의 문장 부분을 낸다. 숫자·표·차트 값은 코드가 채운다.",
    "input_schema": {
        "type": "object",
        "properties": {
            "lead": {"type": "string"},
            "sub": {"type": "string"},
            "lens_insights": {"type": "object", "additionalProperties": {"type": "string"}},
            "muse": {"type": "string"},
            "next": {"type": "array", "items": {"type": "object", "properties": {
                "text": {"type": "string"}, "drilldown": {"type": "boolean"}}}},
        },
        "required": ["lead", "lens_insights", "next"],
    },
}


def user_payload(question: str, bundle_summary: dict) -> str:
    """캐시 밖으로 나가는 가변부. system + tool 은 고정 prefix 로 캐시한다."""
    import json
    return "DATA:\n" + json.dumps({"question": question, **bundle_summary}, ensure_ascii=False)
