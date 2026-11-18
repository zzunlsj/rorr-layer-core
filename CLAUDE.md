# CLAUDE.md — rorr-layer-core

Claude Code / CLI 가 이 레포에서 작업할 때 먼저 읽는 파일. 사람 담당자도 같은 규칙을 따른다.

## 1. 이 레포는 무엇인가

Ask RORR v2(웹 rorr.club/chat 질의응답) 답변 고도화의 **층별 구현 기준**이다.
실서비스 코드가 아니다 — 각 층 담당자가 아래 레포에 옮겨 넣는다.

| 층 | 실서비스 레포 | 이 레포 경로 |
|---|---|---|
| L2 의도 판정 (Jev 라우터) | `piecomp/l3-R-D` | `src/rorr_layer_core/l2/` |
| L3 컨텍스트 조립 (쿼리 생성 · Sonnet) | `piecomp/l3-R-D` | `src/rorr_layer_core/l3/` |
| L4 정형화 · 카드 (Haiku · emit_viz) | `piecomp/rorr-ask-renderer` | `src/rorr_layer_core/l4/` |

## 2. 먼저 읽는 순서

1. `HANDOFF.md` — 지금 어디까지 왔고 다음 할 일이 무엇인지
2. `docs/00-overview.md` — 목업 ↔ 층 매핑, 전체 흐름
3. 맡은 층 문서 `docs/01~03-*.md`
4. `docs/decisions.md` — 확정/제안/미결 결정
5. `contracts/*.schema.json` — 층 사이 계약

## 3. 명령

```bash
python -m pytest -q          # 모든 변경 후 실행. 실패한 채로 커밋하지 않는다
python scripts/demo.py       # 목업 Q1 파이프라인 → 봉투 JSON
python scripts/demo.py --bad # 가드레일 동작 확인
```

## 4. 지켜야 할 규칙

- **숫자는 LLM이 만들지 않는다.** 표·lens 값은 L3 데이터에서, LLM은 문장만. (L4 프롬프트 초안 원칙)
- **서사(역대 기록)는 narrative_fact 카드 문장만.** LLM이 기록을 새로 쓰지 않는다. (D-007)
- **서하 대사에 숫자·지표명 금지, 충전·Boost 권유 금지.** (3채널 UX 원칙, no_dependency)
- **티어·경로 판정에 LLM을 쓰지 않는다.** question_form · subject 는 규칙 기반. (D-003)
- **계약을 바꾸면 세 곳을 같이 고친다:** `contracts/*.schema.json` · `src/rorr_layer_core/contracts.py` · 해당 층 docs. (D-004)
- **intent 추가는 `l2/intents.py` 한 곳에서.** L2·L3 목록이 어긋나지 않게 버전(`INTENT_REGISTRY_VERSION`)을 올린다. (D-002)
- 새 지표를 화면에 내보내려면 `l4/glossary.py METRICS` 에 이름·기준을 먼저 등록한다. (G4)
- 결정을 내리거나 바꾸면 `docs/decisions.md` 에 한 줄 남긴다.
- **세션을 끝낼 때 `HANDOFF.md` 의 '이력'과 '다음 할 일'을 갱신한다.** 다음 세션(사람·Claude)이 이걸 보고 이어간다.

## 5. 실서비스 코드에서 확인된 위치 (Notion 태스크 기준 — 레포 대조 전)

| 무엇 | 위치 | 출처 |
|---|---|---|
| Jev 판정 (domain+topic → intent) | `l3-R-D` `src/embedder/jev.py` `judge_route` (브랜치 `feat/jev-judge`) | [L2] 인텐트 추출 테스트 정리 |
| scope × intent → 테이블 매핑 | `source-mapping.ts` | L3 프로세스 부록 C |
| 소켓 시점 어휘 하드코딩 | `scope.service.ts` | 대화 레이어 구조 구성 §2 |
| L4 정형화기 | `formatter.py` (`formalize()`, 프롬프트 캐싱) | L4 하이쿠 비용 계산 |
| 카드 렌더 | `piecomp/rorr-ask-renderer` | [L4↔웹] 프롬프트 & kind 정리 |

> 위 경로는 아직 실제 코드와 대조하지 않았다 (HANDOFF.md '미확인'). 대조 후 이 표를 고친다.

## 6. 원본 문서

`docs/sources.md` 에 Notion 링크 전체. 수치(원가·정확도)는 원본 문서의 실측값을 인용하고, 바뀌면 원본을 따른다.
