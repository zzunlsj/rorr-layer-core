from rorr_layer_core.energy import charge, margin_krw


def test_rules():
    assert charge("answered")["cost"] == 1
    for o in ("no_data", "l3_failed", "off_domain", "clarify", "system_error"):
        assert charge(o)["cost"] == 0
    assert charge("answered", entry="recommended")["cost"] == 0


def test_margin_tail_is_negative():
    assert margin_krw(42) > 0 and margin_krw(177) < 0
