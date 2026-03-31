import pandas as pd

from modules.comparison import (
    RefinanceVariant,
    build_baseline_result,
    build_display_graph_dataframe,
    build_display_milestone_dataframes,
    build_display_net_balance_graph_dataframe,
    build_display_summary_dataframe,
    build_milestone_dataframes,
    build_variant_result,
    build_variant_results,
    deflate_value,
)


def test_baseline_result_has_no_investment():
    baseline = build_baseline_result(principal=100_000, interest=0.01, term=2)

    assert baseline.is_baseline is True
    assert baseline.name == "Bez refinancování"
    assert baseline.monthly_savings == 0
    assert baseline.final_investment_value == 0
    assert baseline.payoff_month_with_investment is None
    assert baseline.schedule_df["investment_values"].eq(0).all()
    assert baseline.total_tax_savings > 0


def test_variant_result_uses_generated_label_and_summary_metrics():
    variant = RefinanceVariant(refinancing_interest=0.005, new_loan_length=3)

    result = build_variant_result(
        principal=100_000,
        original_interest=0.01,
        original_term=2,
        refinancing_year=1,
        variant=variant,
        risk_choice="safe",
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
        risk_choice="risky",
    )

    graph_df = build_display_graph_dataframe([baseline, variant], refinancing_year=1)
    summary_df = build_display_summary_dataframe([baseline, variant])

    assert "Bez refinancování - zůstatek" in graph_df.columns
    assert "3 let | 0.50 % - zůstatek" in graph_df.columns
    assert "3 let | 0.50 % - investice" not in graph_df.columns
    assert "Bez refinancování - investice" not in graph_df.columns
    assert "3 let | 0.50 % - daňová úspora" not in graph_df.columns
    assert graph_df.loc[12, "Bez refinancování - zůstatek"] > 0
    assert pd.isna(graph_df.loc[13, "Bez refinancování - zůstatek"])
    assert set(summary_df["Scénář"]) == {"Bez refinancování", "3 let | 0.50 %"}
    assert "Průměrná roční daňová úspora" in summary_df.columns
    assert "Měsíc plného doplacení investicí" in summary_df.columns


def test_net_balance_graph_starts_at_negative_principal_and_cuts_off_baseline():
    baseline = build_baseline_result(principal=100_000, interest=0.01, term=2)
    variant = build_variant_result(
        principal=100_000,
        original_interest=0.01,
        original_term=2,
        refinancing_year=1,
        variant=RefinanceVariant(refinancing_interest=0.005, new_loan_length=3),
        risk_choice="risky",
    )

    net_balance_df = build_display_net_balance_graph_dataframe([baseline, variant], refinancing_year=1)

    assert net_balance_df.loc[0, "Bez refinancování"] == -100000
    assert net_balance_df.loc[0, "3 let | 0.50 %"] == -100000
    assert net_balance_df.loc[12, "Bez refinancování"] < 0
    assert pd.isna(net_balance_df.loc[13, "Bez refinancování"])


def test_longer_variant_invests_difference_against_shorter_reference_variant():
    results = build_variant_results(
        principal=2_500_000,
        original_interest=0.0169,
        original_term=30,
        refinancing_year=7,
        variants=[
            RefinanceVariant(refinancing_interest=0.05, new_loan_length=30),
            RefinanceVariant(refinancing_interest=0.05, new_loan_length=37),
        ],
        risk_choice="medium",
    )

    shorter_variant = next(result for result in results if result.loan_length_years == 30)
    longer_variant = next(result for result in results if result.loan_length_years == 37)

    assert shorter_variant.monthly_savings == 0
    assert shorter_variant.final_investment_value > 0
    assert longer_variant.reference_monthly_payment == shorter_variant.monthly_payment
    assert longer_variant.monthly_savings > 0
    assert longer_variant.final_investment_value > 0
    assert longer_variant.total_tax_savings > 0
    assert longer_variant.schedule_df.loc[longer_variant.schedule_df["month"] <= 84, "investment_values"].eq(0).all()
    assert longer_variant.schedule_df.loc[longer_variant.schedule_df["month"] == 85, "investment_values"].iloc[0] > 0
    assert longer_variant.schedule_df["investment_values"].iloc[-1] > 0
    assert shorter_variant.comparison_end_month == longer_variant.comparison_end_month
    assert shorter_variant.variant_end_month < shorter_variant.comparison_end_month


def test_shorter_variant_continues_with_full_payment_investment_after_payoff():
    results = build_variant_results(
        principal=2_500_000,
        original_interest=0.0169,
        original_term=30,
        refinancing_year=7,
        variants=[
            RefinanceVariant(refinancing_interest=0.05, new_loan_length=30),
            RefinanceVariant(refinancing_interest=0.05, new_loan_length=37),
        ],
        risk_choice="medium",
    )
    shorter_variant = next(result for result in results if result.loan_length_years == 30)

    assert shorter_variant.variant_end_month == 360
    assert shorter_variant.comparison_end_month == 444
    assert shorter_variant.schedule_df["month"].max() == 444
    assert shorter_variant.schedule_df.loc[shorter_variant.schedule_df["month"] == 361, "balance"].iloc[0] == 0
    assert shorter_variant.schedule_df.loc[shorter_variant.schedule_df["month"] == 361, "interest"].iloc[0] == 0
    assert (
        shorter_variant.schedule_df.loc[shorter_variant.schedule_df["month"] == 361, "tax_savings_cumulative"].iloc[0]
        == shorter_variant.schedule_df.loc[shorter_variant.schedule_df["month"] == 360, "tax_savings_cumulative"].iloc[0]
    )
    assert (
        shorter_variant.schedule_df.loc[shorter_variant.schedule_df["month"] == 361, "investment_values"].iloc[0]
        > shorter_variant.schedule_df.loc[shorter_variant.schedule_df["month"] == 360, "investment_values"].iloc[0]
    )


def test_zero_inflation_keeps_nominal_and_real_values_equal():
    baseline = build_baseline_result(principal=100_000, interest=0.01, term=2)
    variant = build_variant_result(
        principal=100_000,
        original_interest=0.01,
        original_term=2,
        refinancing_year=1,
        variant=RefinanceVariant(refinancing_interest=0.005, new_loan_length=3),
        risk_choice="safe",
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


def test_real_summary_deflates_final_values():
    results = build_variant_results(
        principal=2_500_000,
        original_interest=0.0169,
        original_term=30,
        refinancing_year=7,
        variants=[
            RefinanceVariant(refinancing_interest=0.05, new_loan_length=30),
            RefinanceVariant(refinancing_interest=0.05, new_loan_length=37),
        ],
        risk_choice="medium",
    )
    longer_variant = next(result for result in results if result.loan_length_years == 37)

    nominal_summary_df = build_display_summary_dataframe([longer_variant], annual_inflation=0.02, display_mode="nominal")
    real_summary_df = build_display_summary_dataframe([longer_variant], annual_inflation=0.02, display_mode="real")

    nominal_milestones = build_display_milestone_dataframes([longer_variant], annual_inflation=0.02, display_mode="nominal")
    real_milestones = build_display_milestone_dataframes([longer_variant], annual_inflation=0.02, display_mode="real")
    assert len(real_milestones) > 0
    nominal_last = nominal_milestones[-1][1]
    real_last = real_milestones[-1][1]
    assert real_last.loc[0, "Investice"] < nominal_last.loc[0, "Investice"]
    assert real_last.loc[0, "Daňová úspora"] < nominal_last.loc[0, "Daňová úspora"]
    assert real_last.loc[0, "Zisk/ztráta"] != nominal_last.loc[0, "Zisk/ztráta"]
    assert real_summary_df.loc[0, "Měsíční splátka"] == deflate_value(
        nominal_summary_df.loc[0, "Měsíční splátka"],
        longer_variant.monthly_payment_month,
        0.02,
    )


def test_net_result_matches_investment_plus_tax_minus_interest():
    results = build_variant_results(
        principal=2_500_000,
        original_interest=0.0169,
        original_term=30,
        refinancing_year=7,
        variants=[
            RefinanceVariant(refinancing_interest=0.05, new_loan_length=30),
            RefinanceVariant(refinancing_interest=0.05, new_loan_length=37),
        ],
        risk_choice="medium",
    )
    longer_variant = next(result for result in results if result.loan_length_years == 37)

    assert longer_variant.net_result == round(
        longer_variant.final_investment_value + longer_variant.total_tax_savings - longer_variant.total_interest, 2
    )


def test_net_result_uses_common_end_horizon_for_shorter_variant():
    results = build_variant_results(
        principal=2_500_000,
        original_interest=0.0169,
        original_term=30,
        refinancing_year=7,
        variants=[
            RefinanceVariant(refinancing_interest=0.05, new_loan_length=30),
            RefinanceVariant(refinancing_interest=0.05, new_loan_length=37),
        ],
        risk_choice="medium",
    )
    shorter_variant = next(result for result in results if result.loan_length_years == 30)

    investment_at_variant_end = float(
        shorter_variant.schedule_df.loc[shorter_variant.schedule_df["month"] == shorter_variant.variant_end_month, "investment_values"].iloc[0]
    )

    assert shorter_variant.final_investment_value > investment_at_variant_end
    assert shorter_variant.net_result == round(
        shorter_variant.final_investment_value + shorter_variant.total_tax_savings - shorter_variant.total_interest, 2
    )


def test_net_result_at_variant_end_uses_variant_payoff_time():
    results = build_variant_results(
        principal=2_500_000,
        original_interest=0.0169,
        original_term=30,
        refinancing_year=7,
        variants=[
            RefinanceVariant(refinancing_interest=0.05, new_loan_length=30),
            RefinanceVariant(refinancing_interest=0.05, new_loan_length=37),
        ],
        risk_choice="medium",
    )
    shorter_variant = next(result for result in results if result.loan_length_years == 30)

    investment_at_variant_end = float(
        shorter_variant.schedule_df.loc[shorter_variant.schedule_df["month"] == shorter_variant.variant_end_month, "investment_values"].iloc[0]
    )
    tax_at_variant_end = float(
        shorter_variant.schedule_df.loc[shorter_variant.schedule_df["month"] == shorter_variant.variant_end_month, "tax_savings_cumulative"].iloc[0]
    )

    assert shorter_variant.net_result_at_variant_end == round(
        investment_at_variant_end + tax_at_variant_end - shorter_variant.total_interest, 2
    )
    assert shorter_variant.net_result > shorter_variant.net_result_at_variant_end
