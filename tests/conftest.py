import json
import pathlib

import pytest

FX = pathlib.Path(__file__).resolve().parents[1] / "fixtures"


@pytest.fixture
def q1():
    return json.loads((FX / "q1_match_review.json").read_text())


@pytest.fixture
def faker_log():
    return json.loads((FX / "faker_log_2026-11-09.json").read_text())
