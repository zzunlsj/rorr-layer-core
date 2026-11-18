"""Muse 메시지 — 서하 한마디가 화면으로 가는 계약과 출력 검사.

대사를 만드는 페르소나 경로(T1 템플릿 · qwen3)는 이 레포 범위 밖이다. 여기에는
그 출력이 지켜야 하는 모양(contracts/muse_message.schema.json)과 검사만 둔다.
"""
from .message import check_message

__all__ = ["check_message"]
