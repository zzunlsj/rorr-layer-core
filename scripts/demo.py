"""목업 Q1(경기 해설)을 L2→L3→L4로 돌려 웹 봉투(JSON)를 출력한다.

    python scripts/demo.py            # 정상 초안
    python scripts/demo.py --bad      # faker 로그 같은 나쁜 초안 → 가드레일이 막는 모습
    python scripts/demo.py --cue      # 같은 질문에서 서하에게 넘기는 재료(muse_cue) — 숫자 없음
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))
from rorr_layer_core.pipeline import run, run_bundle  # noqa: E402

fx = json.loads((pathlib.Path(__file__).resolve().parents[1] / "fixtures/q1_match_review.json").read_text())
if "--cue" in sys.argv:
    print(json.dumps(run_bundle(fx).muse_cue.to_dict(), ensure_ascii=False, indent=2))
else:
    env = run(fx, "draft_bad" if "--bad" in sys.argv else "draft_good")
    print(json.dumps(env.to_dict(), ensure_ascii=False, indent=2))
