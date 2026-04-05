import math
import pandas as pd
from api.models import CalculateRequest, GraphResponse, SummaryResponse, PayoffMarker
from api.formatting import format_currency, format_summary_dataframe, format_milestone_dataframe, rank_refinance_variants
from modules.comparison import (
    RefinanceVariant,
    build_baseline_result,
    build_display_graph_dataframe,
    build_display_milestone_dataframes,
    build_display_summary_dataframe,
    build_variant_results,
)
from modules.investing_strategies import FIXED_INTEREST_RATES


def _compute(req: CalculateRequest):
    """Run all calculations. Returns (results, graph_df, summary_df, milestone_dfs, ranked_df, recommendation)."""
    # IMPORTANT: Don't mutate global FIXED_INTEREST_RATES -- make a local copy
    rates = dict(FIXED_INTEREST_RATES)
    if req.strategy == "custom" and req.custom_rate is not None:
        rates["custom"] = req.custom_rate / 100
        # Temporarily set global for modules that read it
        FIXED_INTEREST_RATES["custom"] = req.custom_rate / 100

    interest_rate = req.rate / 100
    inflation = req.inflation / 100

    results = [build_baseline_result(req.principal, interest_rate, req.term)]

    variant_configs = [
        RefinanceVariant(
            refinancing_interest=v.refinancing_interest / 100,
            new_loan_length=req.term + v.length_change,
            extra_principal=float(v.extra_principal),
        )
        for v in req.variants
    ]

    results.extend(build_variant_results(
        principal=req.principal,
        original_interest=interest_rate,
        original_term=req.term,
        refinancing_year=req.refinancing_year,
        variants=variant_configs,
        risk_choice=req.strategy,
        invest_after_payoff=req.invest_after_payoff,
    ))

    graph_df = build_display_graph_dataframe(results, req.refinancing_year, inflation, req.display_mode)
    summary_df = build_display_summary_dataframe(results, inflation, req.display_mode)
    milestone_dfs = build_display_milestone_dataframes(results, inflation, req.display_mode)
    ranked_df = rank_refinance_variants(summary_df, milestone_dfs)

    # Build recommendation text
    recommendation = None
    if len(ranked_df) >= 2 and milestone_dfs:
        best = ranked_df.iloc[0]
        last_label, last_df = milestone_dfs[-1]
        best_row = last_df[last_df["Scénář"] == best["Scénář"]]
        if not best_row.empty:
            d = best_row.iloc[0]
            recommendation = (
                f"Nejvýhodnější varianta je **{best['Scénář']}** "
                f"se ziskem/ztrátou {format_currency(d['Zisk/ztráta'])} na konci horizontu ({last_label}). "
                "Porovnání je počítané ve stejném horizontu jako nejdelší zadaná varianta; "
                "kratší varianta po splacení hypotéky dál investuje svou bývalou měsíční splátku."
            )
            if pd.notna(best.get("Měsíc plného doplacení investicí")):
                recommendation += f" Investice dorovná hypotéku v měsíci {int(best['Měsíc plného doplacení investicí'])}."

    return results, graph_df, summary_df, milestone_dfs, ranked_df, recommendation


def build_graph_response(req: CalculateRequest) -> GraphResponse:
    results, graph_df, _, _, _, _ = _compute(req)

    months = graph_df.index.tolist()
    series = {}
    for col in graph_df.columns:
        series[col] = [None if (pd.isna(v) or (isinstance(v, float) and math.isnan(v))) else round(v, 2) for v in graph_df[col]]

    # Payoff markers
    payoff_markers = []
    for result in results:
        if result.is_baseline or result.payoff_month_with_investment is None:
            continue
        month = result.payoff_month_with_investment
        row = result.schedule_df.loc[result.schedule_df["month"] == month]
        if not row.empty:
            value = float(row.iloc[0]["investment_values"])
            payoff_markers.append(PayoffMarker(
                x=month, y=value, variant=result.name,
                label=f"Splacení ({month}. m)",
            ))

    return GraphResponse(months=months, series=series, payoff_markers=payoff_markers)


def build_summary_response(req: CalculateRequest) -> SummaryResponse:
    _, _, summary_df, milestone_dfs, ranked_df, recommendation = _compute(req)

    formatted_summary = format_summary_dataframe(summary_df)
    summary_records = formatted_summary.to_dict(orient="records")

    milestones = []
    for label, mdf in milestone_dfs:
        formatted = format_milestone_dataframe(mdf)
        milestones.append({"label": label, "rows": formatted.to_dict(orient="records")})

    ranked = ranked_df.to_dict(orient="records") if not ranked_df.empty else []
    # Convert NaN to None for JSON
    for row in ranked:
        for k, v in row.items():
            if isinstance(v, float) and math.isnan(v):
                row[k] = None

    return SummaryResponse(
        summary=summary_records,
        milestones=milestones,
        recommendation=recommendation,
        ranked_variants=ranked,
    )
