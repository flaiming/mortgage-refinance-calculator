import pytest
import pandas as pd

from modules.comparison import (
    RefinanceVariant,
    best_scenario,
    build_baseline_result,
    build_display_graph_dataframe,
    build_display_milestone_dataframes,
    build_display_summary_dataframe,
    build_variant_result,
    build_variant_results,
    deflate_value,
    monthly_return_rate,
)

DEFAULTS = dict(principal=3_200_000, original_interest=0.023, original_term=30, refinancing_year=5)


def compare(variants, annual_return=0.06, invest_after_payoff=True, **overrides):
    kwargs = {**DEFAULTS, **overrides}
    return build_variant_results(variants=variants, annual_return=annual_return, invest_after_payoff=invest_after_payoff, **kwargs)


def by_length(results, years):
    return next(result for result in results if result.loan_length_years == years)


def final_wealth(result, annual_inflation=0.0):
    """What the household gets: investments at the horizon, tax refunds and the extra cash borrowed."""
    if annual_inflation <= 0:
        return result.final_investment_value + result.total_tax_savings + result.extra_principal
    end = result.comparison_end_month
    refunds = sum(deflate_value(s, (y + 1) * 12, annual_inflation) for y, s in enumerate(result.yearly_tax_savings))
    extra = deflate_value(result.extra_principal, result.refinancing_month, annual_inflation)
    return deflate_value(result.final_investment_value, end, annual_inflation) + refunds + extra


def last_milestone(results, annual_inflation=0.0):
    mode = "real" if annual_inflation > 0 else "nominal"
    return build_display_milestone_dataframes(results, annual_inflation, mode)[-1][1].set_index("Scénář")


def test_baseline_result_has_no_investment():
    baseline = build_baseline_result(principal=100_000, interest=0.01, term=2)

    assert baseline.is_baseline is True
    assert baseline.name == "Bez refinancování"
    assert baseline.monthly_savings == 0
    assert baseline.final_investment_value == 0
    assert baseline.payoff_month_with_investment is None
    assert baseline.schedule_df["investment_values"].eq(0).all()
    assert baseline.total_tax_savings > 0


def test_single_variant_without_budget_invests_nothing():
    result = build_variant_result(
        principal=100_000,
        original_interest=0.01,
        original_term=2,
        refinancing_year=1,
        variant=RefinanceVariant(refinancing_interest=0.005, new_loan_length=3),
        annual_return=0.04,
    )

    assert result.name == "3 let | 0.50 %"
    assert result.loan_length_years == 3
    assert result.monthly_savings == 0
    assert result.final_investment_value == 0
    assert result.schedule_df["month"].iloc[-1] == 36


def test_graph_and_summary_include_baseline_and_variant_columns():
    baseline = build_baseline_result(principal=100_000, interest=0.01, term=2)
    variant = build_variant_result(
        principal=100_000,
        original_interest=0.01,
        original_term=2,
        refinancing_year=1,
        variant=RefinanceVariant(refinancing_interest=0.005, new_loan_length=3),
        annual_return=0.08,
    )

    graph_df = build_display_graph_dataframe([baseline, variant], refinancing_year=1)
    summary_df = build_display_summary_dataframe([baseline, variant])

    assert "Bez refinancování - zůstatek" in graph_df.columns
    assert "3 let | 0.50 % - zůstatek" in graph_df.columns
    assert "3 let | 0.50 % - investice" not in graph_df.columns
    assert "Bez refinancování - investice" not in graph_df.columns
    assert graph_df.loc[12, "Bez refinancování - zůstatek"] > 0
    assert pd.isna(graph_df.loc[13, "Bez refinancování - zůstatek"])
    assert set(summary_df["Scénář"]) == {"Bez refinancování", "3 let | 0.50 %"}
    assert "Průměrná roční daňová úspora" in summary_df.columns
    assert "Měsíc plného doplacení investicí" in summary_df.columns


def test_every_variant_spends_the_same_monthly_budget():
    results = compare(
        [
            RefinanceVariant(0.05, 20),
            RefinanceVariant(0.052, 25),
            RefinanceVariant(0.04, 30),
            RefinanceVariant(0.052, 35, extra_principal=500_000),
        ]
    )
    budget = max(result.monthly_payment for result in results)
    refinancing_month = DEFAULTS["refinancing_year"] * 12
    horizon = max(result.variant_end_month for result in results)

    for result in results:
        df = result.schedule_df
        after = df[df["month"] > refinancing_month]
        assert result.reference_monthly_payment == pytest.approx(budget)
        assert result.comparison_end_month == horizon
        assert int(df["month"].max()) == horizon
        assert (after["payment"] + after["investment_contribution"]).to_numpy() == pytest.approx(budget)
        assert df.loc[df["month"] <= refinancing_month, "investment_contribution"].eq(0).all()


def test_intermediate_variant_keeps_investing_whole_budget_after_payoff():
    """Regression: a variant that invested the difference must not drop to just its former payment."""
    results = compare([RefinanceVariant(0.052, 20), RefinanceVariant(0.052, 25), RefinanceVariant(0.052, 30)])
    middle = by_length(results, 25)
    budget = by_length(results, 20).monthly_payment
    df = middle.schedule_df

    assert middle.monthly_savings == pytest.approx(budget - middle.monthly_payment)
    assert df.loc[df["month"] > middle.variant_end_month, "investment_contribution"].to_numpy() == pytest.approx(budget)


def test_without_investing_after_payoff_freed_payment_is_not_invested():
    results = compare([RefinanceVariant(0.052, 30), RefinanceVariant(0.052, 35)], invest_after_payoff=False)
    shorter = by_length(results, 30)

    assert shorter.final_investment_value == 0
    assert shorter.schedule_df["investment_contribution"].eq(0).all()


def test_ranking_does_not_depend_on_input_order():
    variants = [
        RefinanceVariant(0.052, 30),
        RefinanceVariant(0.052, 30, extra_principal=1_000_000),
        RefinanceVariant(0.052, 35),
    ]
    first = last_milestone(compare(variants))["Čisté náklady"]
    second = last_milestone(compare([variants[1], variants[0], variants[2]]))["Čisté náklady"]

    pd.testing.assert_series_equal(first.sort_index(), second.sort_index())


def test_cheaper_rate_wins_against_longer_term_at_higher_rate():
    """Regression: rate groups used to get different budgets, so a 4 % loan invested nothing."""
    results = compare([RefinanceVariant(0.05, 20), RefinanceVariant(0.04, 30), RefinanceVariant(0.05, 35)])
    table = last_milestone(results)

    assert best_scenario(table.reset_index()) == by_length(results, 30).name


@pytest.mark.parametrize("annual_inflation", [0.0, 0.03])
def test_net_cost_ranks_like_final_wealth(annual_inflation):
    """With equal monthly spending, lower net cost must mean exactly that much more wealth at the horizon."""
    results = compare([RefinanceVariant(0.052, 30), RefinanceVariant(0.052, 35)])
    table = last_milestone(results, annual_inflation)
    shorter, longer = by_length(results, 30), by_length(results, 35)

    cost_diff = table.loc[shorter.name, "Čisté náklady"] - table.loc[longer.name, "Čisté náklady"]
    wealth_diff = final_wealth(longer, annual_inflation) - final_wealth(shorter, annual_inflation)
    assert cost_diff == pytest.approx(wealth_diff, abs=0.01)
    # At a 6 % return beating the ~4.4 % after-tax mortgage rate, extending wins in both views
    assert cost_diff > 0


@pytest.mark.parametrize("annual_inflation", [0.0, 0.03])
def test_net_cost_ranks_like_final_wealth_with_extra_principal_and_different_rates(annual_inflation):
    results = compare(
        [
            RefinanceVariant(0.06, 20),
            RefinanceVariant(0.049, 30, extra_principal=500_000),
            RefinanceVariant(0.052, 30),
            RefinanceVariant(0.052, 35),
        ]
    )
    table = last_milestone(results, annual_inflation)
    reference = results[0]

    for result in results[1:]:
        cost_diff = table.loc[reference.name, "Čisté náklady"] - table.loc[result.name, "Čisté náklady"]
        wealth_diff = final_wealth(result, annual_inflation) - final_wealth(reference, annual_inflation)
        assert cost_diff == pytest.approx(wealth_diff, abs=0.01)


def test_net_cost_is_interest_minus_tax_minus_investment_gain():
    results = compare([RefinanceVariant(0.052, 30), RefinanceVariant(0.052, 35)])
    longer = by_length(results, 35)
    row = last_milestone(results).loc[longer.name]

    assert row["Čisté náklady"] == pytest.approx(
        row["Zaplacené úroky"] - row["Daňová úspora"] - (row["Hodnota investic"] - row["Vloženo do investic"])
    )
    assert longer.net_result == pytest.approx(-row["Čisté náklady"], abs=0.01)


def test_investment_return_is_effective_annual_and_deposit_earns_from_next_month():
    results = compare([RefinanceVariant(0.052, 30), RefinanceVariant(0.052, 35)])
    longer = by_length(results, 35)
    df = longer.schedule_df.set_index("month")
    first = DEFAULTS["refinancing_year"] * 12 + 1

    assert (1 + monthly_return_rate(0.06)) ** 12 == pytest.approx(1.06)
    # The first deposit is not grown in the month it is made
    assert df.loc[first, "investment_values"] == pytest.approx(longer.monthly_savings)
    assert df.loc[first + 12, "investment_values"] - sum(
        longer.monthly_savings * 1.06 ** (k / 12) for k in range(13)
    ) == pytest.approx(0, abs=1e-6)


def test_real_view_counts_only_completed_tax_years():
    results = compare([RefinanceVariant(0.052, 30), RefinanceVariant(0.052, 35)])
    longer = by_length(results, 35)
    from modules.comparison import _extract_at_month

    nominal = _extract_at_month(longer, 354)
    real = _extract_at_month(longer, 354, annual_inflation=1e-12)
    # Month 354 is inside year 30, so only 29 refunds have been received
    assert nominal["tax_cumulative"] == round(sum(longer.yearly_tax_savings[:29]), 2)
    assert real["tax_cumulative"] == pytest.approx(nominal["tax_cumulative"], abs=0.01)
    assert real["inflation_relief"] == pytest.approx(0, abs=0.01)


def test_deflation_uses_elapsed_months():
    assert deflate_value(102, 12, 0.02) == pytest.approx(100)
    assert deflate_value(100, 0, 0.02) == 100


def test_real_summary_and_milestones_are_deflated():
    results = compare([RefinanceVariant(0.052, 30), RefinanceVariant(0.052, 35)])
    longer = by_length(results, 35)

    nominal_summary = build_display_summary_dataframe([longer], 0.02, "nominal")
    real_summary = build_display_summary_dataframe([longer], 0.02, "real")
    nominal_last = last_milestone([longer])
    real_last = last_milestone([longer], 0.02)

    assert real_last.iloc[0]["Hodnota investic"] < nominal_last.iloc[0]["Hodnota investic"]
    assert real_last.iloc[0]["Daňová úspora"] < nominal_last.iloc[0]["Daňová úspora"]
    assert real_last.iloc[0]["Vloženo do investic"] < nominal_last.iloc[0]["Vloženo do investic"]
    assert real_last.iloc[0]["Inflační úleva na jistině"] > 0
    assert "Inflační úleva na jistině" not in nominal_last.columns
    assert real_summary.loc[0, "Měsíční splátka"] == deflate_value(
        nominal_summary.loc[0, "Měsíční splátka"], longer.monthly_payment_month, 0.02
    )
    refunds = [deflate_value(s, (y + 1) * 12, 0.02) for y, s in enumerate(longer.yearly_tax_savings)]
    assert real_summary.loc[0, "Průměrná roční daňová úspora"] == pytest.approx(sum(refunds) / len(refunds), abs=0.01)


def test_zero_inflation_keeps_nominal_and_real_values_equal():
    baseline = build_baseline_result(principal=100_000, interest=0.01, term=2)
    variant = build_variant_result(
        principal=100_000,
        original_interest=0.01,
        original_term=2,
        refinancing_year=1,
        variant=RefinanceVariant(refinancing_interest=0.005, new_loan_length=3),
        annual_return=0.04,
    )

    nominal_graph_df = build_display_graph_dataframe([baseline, variant], refinancing_year=1, annual_inflation=0.0, display_mode="nominal")
    real_graph_df = build_display_graph_dataframe([baseline, variant], refinancing_year=1, annual_inflation=0.0, display_mode="real")
    nominal_summary_df = build_display_summary_dataframe([baseline, variant], annual_inflation=0.0, display_mode="nominal")
    real_summary_df = build_display_summary_dataframe([baseline, variant], annual_inflation=0.0, display_mode="real")

    pd.testing.assert_frame_equal(nominal_graph_df, real_graph_df)
    pd.testing.assert_frame_equal(nominal_summary_df, real_summary_df)


def test_real_display_deflates_values_in_later_months():
    baseline = build_baseline_result(principal=100_000, interest=0.01, term=2)

    nominal_graph_df = build_display_graph_dataframe([baseline], refinancing_year=1, annual_inflation=0.02, display_mode="nominal")
    real_graph_df = build_display_graph_dataframe([baseline], refinancing_year=1, annual_inflation=0.02, display_mode="real")

    assert real_graph_df.loc[12, "Bez refinancování - zůstatek"] < nominal_graph_df.loc[12, "Bez refinancování - zůstatek"]


def test_best_scenario_uses_unrounded_costs():
    table = pd.DataFrame([{"Scénář": "a", "Čisté náklady": 2_045_701.34}, {"Scénář": "b", "Čisté náklady": 2_045_700.56}])
    assert best_scenario(table) == "b"


def test_tiny_payment_difference_is_still_invested():
    results = compare([RefinanceVariant(0.052, 30), RefinanceVariant(0.052, 30, extra_principal=1)])
    cheaper = next(result for result in results if result.extra_principal == 0)

    assert 0 < cheaper.monthly_savings < 0.01
    assert cheaper.schedule_df["investment_contribution"].sum() > 0
