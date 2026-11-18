-- 경기 종료 배치 결과 — 해설형 답의 RORR 분석을 미리 계산해 둔다 (D-006).
-- 질문 시점에는 (game_id, subject_side) 키로 읽기만 → L3 Sonnet 호출 없음, 원가 ≈ ₩0.
-- 생성: rorr_layer_core.l3.match_report.build_match_report (팀별 2행)
CREATE TABLE IF NOT EXISTS match_report_lens (
    game_id          TEXT        NOT NULL,
    subject_side     SMALLINT    NOT NULL CHECK (subject_side IN (100, 200)),
    winprob_curve    JSONB       NOT NULL,          -- [{t, p}] 5~95% 클램프 후
    turning_points   JSONB       NOT NULL,          -- [{t, from, clock, before, after}]
    objective_swing  JSONB       NOT NULL,          -- Top3 [{sequence_index, category, side, swing_gold_60s, intensity, impact}]
    death_breakdown  JSONB,                         -- 결정적 데스 1건 {total_damage, shares[], is_solo}
    report_version   TEXT        NOT NULL DEFAULT 'mr-v1',
    computed_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (game_id, subject_side)
);

-- 입력 조회 (query 조회 가이드 Q1·Q3·Q4 그대로)
-- 한타 승률:  SELECT game_time, win_prob_100 FROM win_probability_frame WHERE game_id = $1 ORDER BY rfc460_timestamp;
--            (subject_side = 200 이면 100 - win_prob_100)
-- 자원 스윙:  SELECT s.*, w.intensity FROM v_objective_swing s LEFT JOIN obj_intensity_weight w USING (category) WHERE s.game_id = $1;
-- 결정적 데스: 주어 팀 데스 중 turning_point 창(±30초) 안에서 가장 먼저 난 킬의 sequence_index →
--            SELECT source, caster_id, total FROM v_kill_damage_breakdown WHERE game_id = $1 AND sequence_index = $2;
