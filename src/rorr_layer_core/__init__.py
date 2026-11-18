"""rorr-layer-core — Ask RORR v2 층별(L2·L3·L4) 구현 기준 코드.

실서비스 코드가 아니라, 각 층 담당자가 자기 레포(l3-R-D, rorr-ask-renderer)에 옮겨 넣을
"기준 구현 + 테스트"다. 순수 함수 위주이고 외부 호출(Jev · Bedrock · DB)은 인터페이스로만 둔다.
"""
from .contracts import CONTRACT_VERSION

__all__ = ["CONTRACT_VERSION"]
