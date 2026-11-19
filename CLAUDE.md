# CLAUDE.md — rorr-layer-core

Claude Code / CLI 가 이 레포에서 작업할 때 먼저 읽는 파일. 사람 담당자도 같은 규칙을 따른다.

## 1. 이 레포는 무엇인가

Ask RORR v2(웹 rorr.club/chat 질의응답) 답변 고도화의 **층별 구현 기준**이다.
실서비스 코드가 아니다 — 각 층 담당자가 아래 레포에 옮겨 넣는다.

| 층 | 실서비스 레포 | 이 레포 경로 |
|---|---|---|
| L2 의도 판정 (Jev 라우터) | `piecomp/rorr-user-intent-router` (`prod` / `dev`) · 호출·scope 는 `piecomp/rorr-socket-server` (`dev`) | `src/rorr_layer_core/l2/` |
| L3 컨텍스트 조립 (쿼리 생성) | `piecomp/rorr-backend-ai` `src/chat/` · `src/rag/` (옛 표기 `rorr-ai-server`) · 프롬프트 측정은 `piecomp/l3-R-D` | `src/rorr_layer_core/l3/` |
| L4 정형화 (Haiku · emit_viz) | `piecomp/rorr-ask-renderer` (`dev` / `prod` 브랜치) | `src/rorr_layer_core/l4/` |
| 화면 렌더 | 웹 프런트 레포 (미확인) — `rorr-ask-renderer` 는 봉투까지만 만든다 | — |

## 2. 먼저 읽는 순서

1. `HANDOFF.md` — 지금 어디까지 왔고 다음 할 일이 무엇인지
2. `docs/00-overview.md` — 목업 ↔ 층 매핑, 전체 흐름
3. `docs/05-current-vs-target.md` — 실서비스 코드의 지금 동작과 층별로 바꿀 것
4. 맡은 층 문서 `docs/01~03-*.md` · 웹/Extension(Muse) 채널 전체 방향은 `docs/06-channels-and-muse.md`
5. `docs/decisions.md` — 확정/제안/미결 결정
6. `contracts/*.schema.json` — 층 사이 계약

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
- **방향의 기준은 Notion 'RORR 기능 명세서'다. 실서비스 코드는 임시 구현이다.** 둘이 다르면 명세 쪽으로 맞춘다. (D-032)
- 결정을 내리거나 바꾸면 `docs/decisions.md` 에 한 줄 남긴다.
- **세션을 끝낼 때 `HANDOFF.md` 의 '이력'과 '다음 할 일'을 갱신한다.** 다음 세션(사람·Claude)이 이걸 보고 이어간다.

## 5. 실서비스 코드 위치 (2026-11-18 레포 대조)

레포 목록 원본: Notion '대화레이어시스템 github 정리' (`docs/sources.md`). 모두 `rorr-repos/` 에 클론 (커밋 안 됨).

| 레포 (`piecomp/`) | 브랜치 · 커밋 | 역할 |
|---|---|---|
| `rorr-user-intent-router` | `prod` `4218e90` (`dev` `bd386c9`) | L2 — Jev 판정 · `POST /route` |
| `rorr-socket-server` | `dev` `f66dd26` (`main` 은 README 뿐) | 소켓 — 라우터 호출 · scope · Energy 턴 |
| `rorr-backend-ai` | `dev` `0fa7b22` (`prod` · `main` 있음) | L3 — 문서의 `rorr-ai-server` 가 이 레포다 |
| `rorr-ask-renderer` | `dev` `9e8ebe7` | L4 |
| `rorr-backend-api-v2` | `dev` `5830d9c` | 백엔드 API — `src/modules/ask/` · Energy 결제 |
| `rorr-ollama-server` | `develop` `7e5d2b0` | 서하 대사 생성 (Ollama) |
| `l3-R-D` | `main` `a1eaf87` | L3 프롬프트 측정 하니스 |

| 무엇 | 위치 | 상태 |
|---|---|---|
| Jev 판정 (domain+topic → intent) | `rorr-user-intent-router` `src/embedder/jev.py:153` `judge_route` · `src/embedder/router.py` | ✅ 위치 확인 |
| 라우터 호출 (`POST /route`) | `rorr-socket-server` `src/gateways/affect-api.service.ts` (`INTENT_ROUTER_URL`) | ✅ 위치 확인 |
| 소켓 시점 어휘 하드코딩 | `rorr-socket-server` `src/gateways/scope.service.ts` (`LIVE_WORDS` 등) | ✅ 위치 확인 |
| L3 흐름 (보정 → RAG → 템플릿 → 쿼리 생성 → L4 호출) | `rorr-backend-ai` `src/chat/chat.service.ts:46` `generate()` · `callCascade` | ✅ 위치 확인 |
| L3 쿼리 생성 | `rorr-backend-ai` `src/chat/bedrock.service.ts:157` `generateQueryPlan` · `src/chat/l3/` (`l3-query.service.ts` · `prompt-builder.ts` · `prompts/*.md` · `query-guard.ts`) | ✅ 위치 확인 |
| scope × intent → 테이블 매핑 | `rorr-backend-ai` `src/chat/source-mapping.ts` · `query-templates.ts` | ✅ 위치 확인 |
| RAG 캐시 · 쿼리 실행 | `rorr-backend-ai` `src/rag/rag.service.ts` (`prepared_questions` · `executeQueryPlan:324` · `bindEntityParams:397`) | ✅ 위치 확인 |
| L3 프롬프트 · 측정 | `l3-R-D` `context/*.md` · `src/prompt-builder.ts` · `stages.json` · `goldset/` | ✅ |
| L4 진입점 | `rorr-ask-renderer` `app.py` `POST /render` · `to_l3()` | ✅ |
| L4 정형화기 | `rorr-ask-renderer` `formatter.py` `formalize()` · `fillable` · `numbers_grounded` · `_downgrade` | ✅ |
| L4 프롬프트 · kind | `rorr-ask-renderer` `prompts.py` (`KIND_ENUM` · `SYSTEM_HEAD` · `EMIT_VIZ_TOOL`) — 소스 오브 트루스 | ✅ |
| L4 표기 변환 | `rorr-ask-renderer` `formatter.py` `_cell_value` · `_col_label` · `_lwrc` · `labels.md` | ✅ |

> 동작 대조 결과는 `docs/05-current-vs-target.md` 와 `docs/01·02` '이식 위치' 표에 있다. 코드를 읽은 것이고 실제 요청으로 확인한 것은 아니다.

## 6. 원본 문서

`docs/sources.md` 에 Notion 링크 전체. 수치(원가·정확도)는 원본 문서의 실측값을 인용하고, 바뀌면 원본을 따른다.
