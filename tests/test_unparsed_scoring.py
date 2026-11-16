"""Unparsed answers: same basis in every mode, and never attributed to a stage in the mode decomposition."""

from msep.eval.experiments import mode_decomposition, plan_sufficiency_by_mode


def _row(iid, mode, valid, ok=True, fam="f1"):
    r = {"instance_id": iid, "family_id": fam, "mode": mode, "gold_class": "INFORMATION_ONLY",
         "sibling_type": "INFORMATION_ONLY", "valid": valid}
    if valid:
        r.update({"detection_correct": ok, "class_correct": ok, "plan_sufficient": ok, "plan_optimal": ok})
    else:
        r.update({"detection_correct": False, "class_correct": False, "plan_sufficient": False, "plan_optimal": False})
    return r


MODES = ("end_to_end", "detection_controlled", "diagnosis_controlled")


def test_unparsed_in_one_mode_is_excluded_not_called_diagnosis():
    rows = [_row("a", "end_to_end", True), _row("a", "detection_controlled", False),
            _row("a", "diagnosis_controlled", True),
            *[_row("b", m, True, fam="f2") for m in MODES]]
    d = mode_decomposition(rows)
    assert d["excluded_unparsed_in_some_mode"] == 1
    assert d["dc_fail_but_dxc_success (diagnosis-attributable)"]["mean"] == 0.0
    assert d["e2e_success"]["mean"] == 1.0


def test_plan_sufficiency_reports_both_bases_in_every_mode():
    rows = [_row("a", m, True) for m in MODES] + [_row("b", m, False, fam="f2") for m in MODES]
    p = plan_sufficiency_by_mode(rows)
    for m in MODES:
        assert p[m]["n"] == 2 and p[m]["unparsed"] == 1
        assert p[m]["all_answers"]["mean"] == 0.5
        assert p[m]["parsed_only"]["mean"] == 1.0
