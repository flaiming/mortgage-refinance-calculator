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
    best_scenario,
)


def _compute(req: CalculateRequest):
    """Run all calculations. Returns (results, graph_df, summary_df, milestone_dfs, ranked_df, recommendation)."""
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
        annual_return=req.annual_return,
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
                f"Nejvýhodnější varianta je **{best['Scénář']}**: čisté náklady "
                f"{format_currency(d['Čisté náklady'])} na konci horizontu ({last_label})"
            )
            runner_up = ranked_df.iloc[1]
            runner_row = last_df[last_df["Scénář"] == runner_up["Scénář"]]
            if not runner_row.empty:
                diff = float(runner_row.iloc[0]["Čisté náklady"]) - float(d["Čisté náklady"])
                recommendation += f", o {format_currency(diff)} méně než **{runner_up['Scénář']}**"
            # Same figure as the summary table, i.e. deflated in real mode
            budget = best.get("Měsíční rozpočet")
            recommendation += (
                ". Všechny varianty počítají se stejným měsíčním rozpočtem"
                + (f" {format_currency(budget)}" if budget else "")
                + ", tedy s nejvyšší z nových splátek. Kdo splácí méně, rozdíl investuje"
            )
            if req.invest_after_payoff:
                recommendation += " a po splacení hypotéky investuje celý rozpočet až do konce nejdelší varianty."
            else:
                recommendation += (
                    ". Po splacení hypotéky se uvolněné peníze neinvestují, "
                    "takže kratší varianty jsou v porovnání znevýhodněné."
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
        column = f"{result.name} - investice"
        if column in graph_df.columns and month in graph_df.index and pd.notna(graph_df.loc[month, column]):
            # Same (possibly deflated) value as the plotted series
            value = float(graph_df.loc[month, column])
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
        milestones.append({"label": label, "rows": formatted.to_dict(orient="records"), "best": best_scenario(mdf)})

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
