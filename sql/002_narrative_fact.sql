-- 역대 서사 카드 (D-007). 지금은 사람이 검증해 등록, P3 이후 auto_derived 카드가 같은 테이블에 들어온다.
CREATE TABLE IF NOT EXISTS narrative_fact (
    fact_id       TEXT PRIMARY KEY,
    kind          TEXT NOT NULL CHECK (kind IN ('streak_break','rivalry','league_rivalry','career','rematch')),
    entity_a      TEXT NOT NULL,              -- team/player id
    entity_b      TEXT,                       -- 상대 id 또는 리그 코드 ('LPL')
    scope         TEXT,                       -- worlds | msi | lck ...
    text          TEXT NOT NULL,              -- 화면에 나가는 문장 (LLM은 고르고 다듬기만)
    basis         TEXT NOT NULL,              -- 기준: 녹아웃/전체 경기, 시작 연도
    source        TEXT NOT NULL,
    status        TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft','verified','retired')),
    verified_by   TEXT,
    valid_from    DATE,
    valid_to      DATE,                       -- 기록이 깨지면 닫고 새 카드
    auto_derived  BOOLEAN NOT NULL DEFAULT false,
    tags          TEXT[] NOT NULL DEFAULT '{}',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS narrative_fact_entity ON narrative_fact (entity_a, entity_b) WHERE status = 'verified';

-- 조회 (질문 엔티티 매칭)
-- SELECT * FROM narrative_fact
--  WHERE status = 'verified' AND entity_a = ANY($1)
--    AND (entity_b IS NULL OR entity_b = ANY($1) OR entity_b = ANY($2))   -- $2 = 상대 팀 리그 코드
--    AND (valid_from IS NULL OR valid_from <= current_date)
--    AND (valid_to   IS NULL OR valid_to   >= current_date)
--  ORDER BY (entity_b IS NOT NULL) DESC LIMIT 1;
