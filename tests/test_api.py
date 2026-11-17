from concurrent.futures import ThreadPoolExecutor

import pytest
from pydantic import ValidationError

from api.models import CalculateRequest
from api.services import build_summary_response


@pytest.mark.parametrize(
    "payload",
    [
        {"term": 30, "refinancing_year": 29, "variants": [{"refinancing_interest": 5, "length_change": -1}]},
        {"term": 2, "refinancing_year": 2},
        {"rate": 100.1},
        {"strategy": "custom", "custom_rate": 1_000_000},
        {"strategy": "custom", "custom_rate": None},
        {"variants": []},
    ],
)
def test_invalid_inputs_are_rejected_before_calculation(payload):
    with pytest.raises(ValidationError):
        CalculateRequest(**payload)


def test_custom_return_does_not_leak_between_requests():
    def final_rows(rate):
        return str(build_summary_response(CalculateRequest(strategy="custom", custom_rate=rate)).milestones[-1]["rows"])

    with ThreadPoolExecutor(max_workers=8) as pool:
        rows = list(pool.map(final_rows, [0, 8] * 6))
    assert len(set(rows[0::2])) == 1 and len(set(rows[1::2])) == 1
    assert rows[0] != rows[1]


def test_milestones_name_the_best_variant():
    data = build_summary_response(CalculateRequest())
    assert data.milestones[-1]["best"] == data.ranked_variants[0]["Scénář"]


def test_real_mode_recommendation_quotes_the_displayed_budget():
    data = build_summary_response(CalculateRequest(display_mode="real", inflation=2))
    budget = next(row for row in data.summary if row["Scénář"] != "Bez refinancování")["Měsíční rozpočet"]
    assert f"rozpočtem {budget}" in data.recommendation
