# rorr-layer-core

Ask RORR v2 — **"질문 1개 = 1 Energy(약 ₩120)를 낼 만한 '왜'를 설명하는 해설"** 을 만들기 위한
L2 · L3 · L4 층별 **구현 기준 문서 + 기준 코드 + 테스트**.

- 목업: [Ask RORR 답변 고도화 목업](https://claude.ai/artifact/GkAP1m7xpHqFKSZwCfuFwt)
- 방향성: Notion [Ask RORR 대화 퀄리티 고도화](https://app.notion.com/p/418bc2f961aa807082edd6e9d7a6ff56) → '답변 고도화 방향성'
- 실서비스 코드는 각 층 레포에 있다. 이 레포는 그 레포들에 옮겨 넣을 **기준**이다.
  - L2 → Jev 라우터 레포 (미확인 — `docs/decisions.md` D-013)
  - L3 → `rorr-backend-ai` (`src/chat/` · `src/rag/`) · 프롬프트·측정은 `piecomp/l3-R-D`
  - L4 정형화 → `piecomp/rorr-ask-renderer` · 화면 렌더는 웹 프런트

## 답변 구조 (목업 = 계약)

```
① 결론 한 줄      lead      질문한 주어 관점 고정 · 지표는 이름과 함께          ← L4 (LLM 문장 + 가드레일)
Ⓗ 역대 맥락       history   검증된 서사 카드만 · 2026 밖의 서사                 ← L3 (narrative_fact)
② 사실 카드       facts     기존 kind (스코어 · KDA · 일정)                    ← L3 쿼리 → L4 emit_viz
③ RORR 분석       lenses    한타 승률 · 자원 스윙 · 데스 분해 · LwRC+ · 매치업  ← L3 (경기 종료 배치 + 쿼리)
④ 근거 · 다음     evidence · next   후속 질문 비용 표시 (서하 한마디는 봉투 밖 — 별도 Muse 메시지)   ← L4
   + energy       답변 완료 후 1 차감 · 실패/도메인 밖/되묻기 0 · 탭·추천 질문 무료    ← 백엔드
```

## 층별로 무엇이 바뀌나

| 층 | 레포 | 이 레포의 기준 코드 | 핵심 변경 | 문서 |
|---|---|---|---|---|
| L2 의도 | rorr-user-intent-router (+ rorr-socket-server) | `src/rorr_layer_core/l2/` | intent 레지스트리 단일화 · question_form(왜/어때) · 주어·극성 · 해설형 intent 승격 · 버려지던 필드 전달 | [docs/01-L2-intent.md](docs/01-L2-intent.md) |
| L3 조립 | rorr-backend-ai (+ l3-R-D 측정) | `src/rorr_layer_core/l3/` | 경기 종료 배치(match_report_lens) · lens 레지스트리 · 서사 카드 · L3Bundle(출처·원가·outcome) | [docs/02-L3-context.md](docs/02-L3-context.md) |
| L4 생성 | rorr-ask-renderer | `src/rorr_layer_core/l4/` | 표기 사전 · 가드레일 G1~G10 · AnswerEnvelope v2 · emit_answer 프롬프트 | [docs/03-L4-answer.md](docs/03-L4-answer.md) |
| 공통 | 백엔드 | `energy.py` | Energy 차감 규칙 | [docs/04-energy.md](docs/04-energy.md) |

## 빠른 시작

```bash
python -m pip install -e ".[dev]"
python -m pytest -q                 # 26 tests
python scripts/demo.py              # 목업 Q1을 L2→L3→L4로 → 웹 봉투 JSON
python scripts/demo.py --bad        # faker 로그 같은 초안 → 가드레일이 고치는 모습
```

## 폴더

```
contracts/   층 사이 JSON 스키마 (L2 route v2 · L3 bundle · answer envelope · narrative_fact)
sql/         새 테이블 DDL (match_report_lens · narrative_fact) + 입력 조회
src/         층별 기준 구현 (순수 함수, 외부 호출 없음)
fixtures/    목업 Q1 데이터 · faker 질의 로그(2026-11-09) 발췌
tests/       층별 테스트 — faker 로그 문제 재현 포함
docs/        층별 구현 문서 · 결정 로그 · 태스크 초안 · 원본 링크
CLAUDE.md    Claude Code / CLI 가 이 레포에서 일할 때 읽는 규칙
HANDOFF.md   작업 이력과 다음 할 일 (세션 인계)
```
