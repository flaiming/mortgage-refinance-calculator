import pandas as pd


def format_currency(value: float) -> str:
    return f"{int(round(value)):,}".replace(",", " ") + " Kč"


def format_payoff_month(value: float | None) -> str:
    if pd.isna(value):
        return "Nedosaženo"
    return str(int(value))


def format_summary_dataframe(summary_df):
    formatted_df = summary_df.copy()
    currency_columns = [
        "Měsíční splátka",
        "Měsíční úspora",
        "Referenční splátka pro investici",
        "Průměrná roční daňová úspora",
    ]
    for column in currency_columns:
        if column in formatted_df.columns:
            formatted_df[column] = formatted_df[column].map(lambda value: "-" if pd.isna(value) else format_currency(value))
    if "Měsíc plného doplacení investicí" in formatted_df.columns:
        formatted_df["Měsíc plného doplacení investicí"] = formatted_df["Měsíc plného doplacení investicí"].map(format_payoff_month)
    if "Délka hypotéky [roky]" in formatted_df.columns:
        formatted_df["Délka hypotéky [roky]"] = formatted_df["Délka hypotéky [roky]"].map(lambda value: str(int(value)))
    return formatted_df


def format_milestone_dataframe(milestone_df):
    formatted_df = milestone_df.copy()
    for column in ["Zaplacené úroky", "Zbývající dluh", "Investice", "Daňová úspora", "Bilance", "Zisk/ztráta"]:
        if column in formatted_df.columns:
            formatted_df[column] = formatted_df[column].map(lambda value: "-" if pd.isna(value) else format_currency(value))
    return formatted_df


def rank_refinance_variants(
    summary_df: pd.DataFrame,
    milestone_dfs: list[tuple[str, pd.DataFrame]],
) -> pd.DataFrame:
    refinance_df = summary_df[summary_df["Scénář"] != "Bez refinancování"].copy()
    if refinance_df.empty or not milestone_dfs:
        return refinance_df

    # Use the last milestone (common horizon) for ranking
    last_milestone_df = milestone_dfs[-1][1]
    refinance_df = refinance_df.merge(
        last_milestone_df[["Scénář", "Zisk/ztráta", "Investice"]],
        on="Scénář",
        how="left",
        suffixes=("", "_horizon"),
    )

    payoff_rank_month = refinance_df["Měsíc plného doplacení investicí"].where(
        refinance_df["Měsíc plného doplacení investicí"].notna(),
        float("inf"),
    )
    refinance_df = refinance_df.assign(
        _payoff_rank_month=payoff_rank_month,
        _has_payoff=refinance_df["Měsíc plného doplacení investicí"].notna(),
    )
    refinance_df = refinance_df.sort_values(
        by=["Zisk/ztráta", "_has_payoff", "_payoff_rank_month", "Investice"],
        ascending=[False, False, True, False],
    ).reset_index(drop=True)
    refinance_df["Pořadí"] = range(1, len(refinance_df) + 1)
    refinance_df["Doporučeno"] = refinance_df["Pořadí"] == 1
    return refinance_df.drop(columns=["_payoff_rank_month", "_has_payoff", "Zisk/ztráta", "Investice"])
