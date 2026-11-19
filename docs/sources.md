# 원본 문서 · 레포

## Notion
- 방향성 · 목업 링크: [Ask RORR 대화 퀄리티 고도화](https://app.notion.com/p/418bc2f961aa807082edd6e9d7a6ff56)
- 품질 문제 원문: [faker 최근 경기 질의 로그](https://app.notion.com/p/413bc2f961aa81359a53fddc606aea1b) · [대화레이어 파이프라인 로그 목록](https://app.notion.com/p/410bc2f961aa807e8b04d881677d1630)
- 전체 구조: [대화 레이어 구조 구성 (Web/Extension 소스 증가)](https://app.notion.com/p/401bc2f961aa804490b1f863fcdaf2e4) · [Ask RORR Chat 프로세스](https://app.notion.com/p/3f9bc2f961aa80ee87c9c7856450f353)
- Muse · 채널 (docs/06 의 근거): [Muse 대화 시스템 레이어 구조](https://app.notion.com/p/383bc2f961aa8128806bd8eb58978711) · [L4 표현·변주 레이어 — 동작 흐름](https://app.notion.com/p/3f7bc2f961aa80edace1ddd3ae6eefe3) · [정보·감정 전달 3채널 UX 원칙](https://app.notion.com/p/3cdbc2f961aa81ca91c6ec68f47943f3) · [Muse - 발화](https://app.notion.com/p/3e2bc2f961aa8099bd42f12645cbd3ea) · [친밀도 단계](https://app.notion.com/p/383bc2f961aa81cb9781f6f67f39d92c) · [Fan심 - Draft](https://app.notion.com/p/3a5bc2f961aa8070b1c0cbf261ddde08) · [Muse - 대화 History](https://app.notion.com/p/3ffbc2f961aa805a9e92d844d2ee5301) (맥락 기억 구조 초안 — 2026-11-18 작성) · [RORR 기능 명세서](https://app.notion.com/p/2f8bc2f961aa80719310efc6ba2f3e58)
- L2: [[L2] 인텐트 추출 테스트 정리](https://app.notion.com/p/408bc2f961aa80d7805fe2b934a2881a)
- L3: [L3 프로세스](https://app.notion.com/p/406bc2f961aa8031b635c3db7fd3989a) · [[L3] 쏘넷 5.5 비용](https://app.notion.com/p/410bc2f961aa8053a8bbec1c7f5c00fc)
- L4: [L4 프롬포트 테스트 초안](https://app.notion.com/p/40cbc2f961aa80aa8c9eec50a5576202) · [L4 하이쿠 비용 계산](https://app.notion.com/p/410bc2f961aa80518fdcf2ed468e2248) · [intent별 카드 컴포넌트 확정](https://app.notion.com/p/40fbc2f961aa80f9b865cef6c2c9db51)
- 데이터: [LoL Ontology](https://app.notion.com/p/36dbc2f961aa80c8a1e7cd5524ab65e9) · [query 조회 가이드](https://app.notion.com/p/397bc2f961aa8071b7d2cacff9e896bc) · [neo4j schema](https://app.notion.com/p/3c8bc2f961aa80568646f214df597aa0) · [LwRC+ 기능 명세서](https://app.notion.com/p/411bc2f961aa817db12ef743eec6d48f)
- 개발자 검토용 정리 (docs/05 · 06 을 옮긴 것): [Ask RORR/Muse 층별 구현 검토 자료](https://app.notion.com/p/41cbc2f961aa8078a1d4d8a1d030aee6) (태스크 DB — 2026-11-19 에 이 위치로 옮김. 옛 위치: [참고 페이지](https://app.notion.com/p/41cbc2f961aa81628b0dc3ab4e6e1040)) — 웹 Ask RORR 에서 전체 시스템(웹 · 확장 Muse · Overlay)으로 넓혔다. 하위에 L2 · L3 · L4 · Energy 문서. 방향성 페이지 맨 위에 링크
- 레포 목록: [대화레이어시스템 github 정리](https://app.notion.com/p/41cbc2f961aa800194b7d1554579363a) — `piecomp/` 6개 레포 주소·권한. 위치 대조는 `CLAUDE.md §5`
- DB: [마일스톤 DB](https://app.notion.com/p/311bc2f961aa81588d6cd93de70587a7) · [태스크 DB](https://app.notion.com/p/311bc2f961aa81b6a6eec6dc03ea7044)

## 목업
- [Ask RORR 답변 고도화 목업](https://claude.ai/artifact/GkAP1m7xpHqFKSZwCfuFwt) (Jun 계정 비공개 — 공유는 페이지에서)

## 레포
- L2: `piecomp/rorr-user-intent-router` (`prod` / `dev`) · 소켓 `piecomp/rorr-socket-server` (`dev`) · 백엔드 `piecomp/rorr-backend-api-v2` (`dev`) — D-020
- L3 실서비스: `piecomp/rorr-backend-ai` (`dev`) · L3 프롬프트·측정·정답셋: `piecomp/l3-R-D` (`main`)
- L4 정형화: `piecomp/rorr-ask-renderer` (`dev` → `prod`) · 화면 렌더: 웹 프런트 레포 (미확인)
- 참고: `piecomp/rorr-datacenter-teams-bot` — `l3-R-D` 의 라우팅·예시 프롬프트 출처
- LwRC+ 계산: `zzunlsj/rorr-lwrc` (private) · 조회 페이지 https://zzunlsj.github.io/rorr-lwrc-web/
