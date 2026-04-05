from dataclasses import dataclass

import pandas as pd
from mortgage import Loan

from modules.investor import InvestmentData, Investor
from modules.investing_strategies import FIXED_INTEREST_RATES
from modules.loan_with_refinancing import LoanWithRefinancing
from modules.taxes import Taxes


@dataclass
class RefinanceVariant:
    refinancing_interest: float
    new_loan_length: int
    extra_principal: float = 0.0

    def label(self) -> str:
        parts = [f"{self.new_loan_length} let | {self.refinancing_interest * 100:.2f} %"]
        if self.extra_principal > 0:
            parts.append(f"+{int(self.extra_principal):,}".replace(",", " ") + " Kč")
        return " | ".join(parts)


@dataclass
class ScenarioResult:
    name: str
    initial_principal: float
    schedule_df: pd.DataFrame
    monthly_payment: float
    monthly_payment_month: int
    monthly_savings: float
    monthly_savings_month: int
    total_interest: float
    loan_length_years: int
    final_investment_value: float
    payoff_month_with_investment: int | None
    yearly_tax_savings: list[float]
    max_yearly_tax_savings: float
    max_yearly_tax_savings_month: int | None
    average_yearly_tax_savings: float
    average_yearly_tax_savings_month: int | None
    total_tax_savings: float
    tax_savings_at_variant_end: float
    investment_value_at_variant_end: float
    net_result_at_variant_end: float
    net_result: float
    variant_end_month: int
    comparison_end_month: int
    reference_monthly_payment: float | None = None
    is_baseline: bool = False


def monthly_inflation_rate(annual_inflation: float) -> float:
    return (1 + annual_inflation) ** (1 / 12) - 1


def deflate_value(value: float | None, month: int, annual_inflation: float) -> float | None:
    if value is None or pd.isna(value):
        return None
    monthly_rate = monthly_inflation_rate(annual_inflation)
    return float(value) / ((1 + monthly_rate) ** max(month - 1, 0))


def _first_payoff_month(schedule_df: pd.DataFrame) -> int | None:
    reached_balance = schedule_df["investment_values"] >= schedule_df["balance"]
    if not reached_balance.any():
        return None
    return int(schedule_df.loc[reached_balance, "month"].iloc[0])


def _schedule_df_from_installments(installments: list, risk_choice: str) -> pd.DataFrame:
    rows = []
    for installment in installments:
        rows.append(
            {
                "month": int(installment.number),
                "payment": float(installment.payment),
                "interest": float(installment.interest),
                "principal": float(installment.principal),
                "total_interest": float(installment.total_interest),
                "balance": float(installment.balance),
                "investment_values": float(installment.investment_values.get(risk_choice, 0)),
            }
        )
    return pd.DataFrame(rows)


def _build_tax_columns(schedule_df: pd.DataFrame) -> tuple[pd.DataFrame, list[float]]:
    updated_df = schedule_df.copy()
    taxes = Taxes(updated_df["interest"].tolist())
    yearly_tax_savings = taxes.calculate_yearly_tax_savings()
    cumulative_tax_values = []
    for month in updated_df["month"]:
        completed_years = int(month) // 12
        cumulative_tax_values.append(round(sum(yearly_tax_savings[:completed_years]), 2))
    updated_df["tax_savings_cumulative"] = cumulative_tax_values
    return updated_df, yearly_tax_savings


def _extend_variant_to_common_horizon(
    result: ScenarioResult,
    common_end_month: int,
    risk_choice: str,
    invest_after_payoff: bool = True,
) -> ScenarioResult:
    variant_end_month = int(result.schedule_df["month"].max())
    if variant_end_month >= common_end_month:
        result.comparison_end_month = variant_end_month
        result.variant_end_month = variant_end_month
        result.final_investment_value = float(result.schedule_df["investment_values"].iloc[-1])
        result.net_result = round(result.final_investment_value + result.total_tax_savings - result.total_interest, 2)
        return result

    extended_df = result.schedule_df.copy()
    last_tax_savings = float(extended_df["tax_savings_cumulative"].iloc[-1])
    current_investment_value = float(extended_df["investment_values"].iloc[-1])
    monthly_rate = FIXED_INTEREST_RATES[risk_choice] / 12
    monthly_contribution = float(result.monthly_payment) if invest_after_payoff else 0.0
    additional_rows = []
    for month in range(variant_end_month + 1, common_end_month + 1):
        current_investment_value = (current_investment_value + monthly_contribution) * (1 + monthly_rate)
        additional_rows.append(
            {
                "month": month,
                "payment": 0.0,
                "interest": 0.0,
                "principal": 0.0,
                "total_interest": float(extended_df["total_interest"].iloc[-1]),
                "balance": 0.0,
                "investment_values": float(int(current_investment_value)),
                "tax_savings_cumulative": last_tax_savings,
            }
        )

    if additional_rows:
        extended_df = pd.concat([extended_df, pd.DataFrame(additional_rows)], ignore_index=True)

    result.schedule_df = extended_df
    result.variant_end_month = variant_end_month
    result.comparison_end_month = common_end_month
    result.final_investment_value = float(extended_df["investment_values"].iloc[-1])
    result.net_result = round(result.final_investment_value + result.total_tax_savings - result.total_interest, 2)
    return result


def _apply_variant_comparison_investment(
    schedule_df: pd.DataFrame,
    monthly_savings_vs_reference: float,
    risk_choice: str,
    investment_start_month: int,
) -> pd.DataFrame:
    updated_df = schedule_df.copy()
    updated_df["investment_values"] = 0.0

    if monthly_savings_vs_reference <= 0:
        return updated_df

    yearly_rate = FIXED_INTEREST_RATES[risk_choice]
    investor = Investor(
        invest_data=InvestmentData(),
        monthly_invest=float(monthly_savings_vs_reference),
        yearly_interest_rates={"risky": yearly_rate, "medium": yearly_rate, "safe": yearly_rate},
    )
    investment_values = []
    for month in updated_df["month"]:
        if int(month) < investment_start_month:
            investment_values.append(0.0)
            continue
        risky, medium, safe = investor.add_investment()
        investment_values.append(risky)

    updated_df["investment_values"] = investment_values
    return updated_df


def build_baseline_result(principal: float, interest: float, term: int) -> ScenarioResult:
    loan = Loan(principal=principal, interest=interest, term=term)
    schedule = loan.schedule()[1:]
    schedule_df = pd.DataFrame(
        [
            {
                "month": int(part.number),
                "payment": float(part.payment),
                "interest": float(part.interest),
                "principal": float(part.principal),
                "total_interest": float(part.total_interest),
                "balance": float(part.balance),
                "investment_values": 0.0,
            }
            for part in schedule
        ]
    )
    schedule_df, yearly_tax_savings = _build_tax_columns(schedule_df)
    max_yearly_tax_savings = max(yearly_tax_savings, default=0.0)
    average_yearly_tax_savings = round(sum(yearly_tax_savings) / len(yearly_tax_savings), 2) if yearly_tax_savings else 0.0
    max_yearly_tax_savings_month = (yearly_tax_savings.index(max_yearly_tax_savings) + 1) * 12 if yearly_tax_savings else None
    average_yearly_tax_savings_month = int(round(sum((index + 1) * 12 for index, _ in enumerate(yearly_tax_savings)) / len(yearly_tax_savings))) if yearly_tax_savings else None

    return ScenarioResult(
        name="Bez refinancování",
        initial_principal=float(principal),
        schedule_df=schedule_df,
        monthly_payment=float(schedule[0].payment),
        monthly_payment_month=1,
        monthly_savings=0.0,
        monthly_savings_month=1,
        total_interest=float(schedule_df["interest"].sum()),
        loan_length_years=term,
        final_investment_value=0.0,
        payoff_month_with_investment=None,
        yearly_tax_savings=yearly_tax_savings,
        max_yearly_tax_savings=max_yearly_tax_savings,
        max_yearly_tax_savings_month=max_yearly_tax_savings_month,
        average_yearly_tax_savings=average_yearly_tax_savings,
        average_yearly_tax_savings_month=average_yearly_tax_savings_month,
        total_tax_savings=round(sum(yearly_tax_savings), 2),
        tax_savings_at_variant_end=float(schedule_df["tax_savings_cumulative"].iloc[-1]),
        investment_value_at_variant_end=0.0,
        net_result_at_variant_end=round(float(schedule_df["tax_savings_cumulative"].iloc[-1]) - float(schedule_df["interest"].sum()), 2),
        net_result=round(0.0 + round(sum(yearly_tax_savings), 2) - float(schedule_df["interest"].sum()), 2),
        variant_end_month=int(schedule_df["month"].max()),
        comparison_end_month=int(schedule_df["month"].max()),
        reference_monthly_payment=None,
        is_baseline=True,
    )


def build_variant_result(
    principal: float,
    original_interest: float,
    original_term: int,
    refinancing_year: int,
    variant: RefinanceVariant,
    risk_choice: str,
    reference_monthly_payment: float | None = None,
) -> ScenarioResult:
    loan = LoanWithRefinancing(
        principal=principal,
        interest=original_interest,
        term=original_term,
        refinancing_year=refinancing_year,
        refinancing_interest=variant.refinancing_interest,
        new_hypo_length_change_years=variant.new_loan_length - original_term,
        enable_investments=False,
        extra_principal=variant.extra_principal,
    )
    schedule = loan.schedule_with_refinancing()
    schedule_df = _schedule_df_from_installments(schedule, risk_choice)
    monthly_savings = 0.0 if reference_monthly_payment is None else max(0.0, reference_monthly_payment - float(loan.new_monthly_payment))
    schedule_df = _apply_variant_comparison_investment(
        schedule_df,
        monthly_savings,
        risk_choice,
        investment_start_month=refinancing_year * 12 + 1,
    )
    schedule_df, yearly_tax_savings = _build_tax_columns(schedule_df)
    max_yearly_tax_savings = max(yearly_tax_savings, default=0.0)
    average_yearly_tax_savings = round(sum(yearly_tax_savings) / len(yearly_tax_savings), 2) if yearly_tax_savings else 0.0
    max_yearly_tax_savings_month = (yearly_tax_savings.index(max_yearly_tax_savings) + 1) * 12 if yearly_tax_savings else None
    average_yearly_tax_savings_month = int(round(sum((index + 1) * 12 for index, _ in enumerate(yearly_tax_savings)) / len(yearly_tax_savings))) if yearly_tax_savings else None

    return ScenarioResult(
        name=variant.label(),
        initial_principal=float(principal),
        schedule_df=schedule_df,
        monthly_payment=float(loan.new_monthly_payment),
        monthly_payment_month=refinancing_year * 12 + 1,
        monthly_savings=float(monthly_savings),
        monthly_savings_month=refinancing_year * 12 + 1,
        total_interest=float(schedule_df["interest"].sum()),
        loan_length_years=variant.new_loan_length,
        final_investment_value=float(schedule_df["investment_values"].iloc[-1]),
        payoff_month_with_investment=_first_payoff_month(schedule_df) if monthly_savings > 0 else None,
        yearly_tax_savings=yearly_tax_savings,
        max_yearly_tax_savings=max_yearly_tax_savings,
        max_yearly_tax_savings_month=max_yearly_tax_savings_month,
        average_yearly_tax_savings=average_yearly_tax_savings,
        average_yearly_tax_savings_month=average_yearly_tax_savings_month,
        total_tax_savings=round(sum(yearly_tax_savings), 2),
        tax_savings_at_variant_end=float(schedule_df["tax_savings_cumulative"].iloc[-1]),
        investment_value_at_variant_end=float(schedule_df["investment_values"].iloc[-1]),
        net_result_at_variant_end=round(
            float(schedule_df["investment_values"].iloc[-1])
            + float(schedule_df["tax_savings_cumulative"].iloc[-1])
            - float(schedule_df["interest"].sum()),
            2,
        ),
        net_result=round(float(schedule_df["investment_values"].iloc[-1]) + round(sum(yearly_tax_savings), 2) - float(schedule_df["interest"].sum()), 2),
        variant_end_month=int(schedule_df["month"].max()),
        comparison_end_month=int(schedule_df["month"].max()),
        reference_monthly_payment=reference_monthly_payment,
        is_baseline=False,
    )


def build_variant_results(
    principal: float,
    original_interest: float,
    original_term: int,
    refinancing_year: int,
    variants: list[RefinanceVariant],
    risk_choice: str,
    invest_after_payoff: bool = True,
) -> list[ScenarioResult]:
    results_by_group: list[ScenarioResult] = []
    grouped_variants: dict[float, list[RefinanceVariant]] = {}
    for variant in variants:
        grouped_variants.setdefault(variant.refinancing_interest, []).append(variant)

    for _, group_variants in grouped_variants.items():
        sorted_variants = sorted(group_variants, key=lambda item: item.new_loan_length)
        reference_result = build_variant_result(
            principal=principal,
            original_interest=original_interest,
            original_term=original_term,
            refinancing_year=refinancing_year,
            variant=sorted_variants[0],
            risk_choice=risk_choice,
            reference_monthly_payment=None,
        )
        results_by_group.append(reference_result)

        reference_monthly_payment = reference_result.monthly_payment
        for variant in sorted_variants[1:]:
            results_by_group.append(
                build_variant_result(
                    principal=principal,
                    original_interest=original_interest,
                    original_term=original_term,
                    refinancing_year=refinancing_year,
                    variant=variant,
                    risk_choice=risk_choice,
                    reference_monthly_payment=reference_monthly_payment,
                )
            )

    common_end_month = max((int(result.schedule_df["month"].max()) for result in results_by_group), default=0)
    results_by_group = [
        _extend_variant_to_common_horizon(result, common_end_month, risk_choice, invest_after_payoff)
        for result in results_by_group
    ]

    sorted_results = sorted(results_by_group, key=lambda result: (result.schedule_df["month"].iloc[0], result.loan_length_years, result.name))

    # Deduplicate names by appending a counter suffix
    name_counts: dict[str, int] = {}
    for result in sorted_results:
        count = name_counts.get(result.name, 0) + 1
        name_counts[result.name] = count
    seen: dict[str, int] = {}
    for result in sorted_results:
        base_name = result.name
        seen[base_name] = seen.get(base_name, 0) + 1
        if name_counts[base_name] > 1:
            result.name = f"{base_name} ({seen[base_name]})"

    return sorted_results


def build_graph_dataframe(results: list[ScenarioResult], refinancing_year: int | None = None) -> pd.DataFrame:
    graph_data: dict[str, pd.Series] = {}
    refinancing_cutoff_month = None if refinancing_year is None else refinancing_year * 12
    for result in results:
        schedule_df = result.schedule_df.set_index("month")
        balance_series = schedule_df["balance"]
        if result.is_baseline and refinancing_cutoff_month is not None:
            balance_series = balance_series.where(balance_series.index <= refinancing_cutoff_month)
        balance_series = balance_series.copy()
        balance_series[balance_series <= 0] = float("nan")
        graph_data[f"{result.name} - zůstatek"] = balance_series
        if not result.is_baseline and schedule_df["investment_values"].max() > 0:
            inv_series = schedule_df["investment_values"].copy()
            inv_series[inv_series <= 0] = float("nan")
            graph_data[f"{result.name} - investice"] = inv_series

    graph_df = pd.DataFrame(graph_data)
    graph_df.index.name = "Měsíc"
    return graph_df.sort_index()


def build_display_graph_dataframe(
    results: list[ScenarioResult],
    refinancing_year: int | None = None,
    annual_inflation: float = 0.0,
    display_mode: str = "nominal",
) -> pd.DataFrame:
    graph_df = build_graph_dataframe(results, refinancing_year=refinancing_year)
    if display_mode != "real":
        return graph_df

    real_graph_df = graph_df.copy()
    for column in real_graph_df.columns:
        real_graph_df[column] = [
            deflate_value(value, month, annual_inflation)
            for month, value in zip(real_graph_df.index, real_graph_df[column])
        ]
    return real_graph_df



def _extract_at_month(
    result: ScenarioResult,
    month: int,
    annual_inflation: float = 0.0,
) -> dict:
    """Extract metrics for a single result at a given month.

    When annual_inflation > 0, cumulative values (interest, tax savings) are
    computed as sums of individually deflated payments, while point-in-time
    values (balance, investment) are deflated to month 0.
    """
    df = result.schedule_df
    row = df.loc[df["month"] == month]
    if row.empty:
        return {
            "balance": None,
            "investment": None,
            "tax_cumulative": None,
            "interest_cumulative": None,
        }
    row = row.iloc[0]

    if annual_inflation <= 0:
        return {
            "balance": float(row["balance"]),
            "investment": float(row["investment_values"]),
            "tax_cumulative": float(row["tax_savings_cumulative"]),
            "interest_cumulative": float(df.loc[df["month"] <= month, "interest"].sum()),
        }

    # Point-in-time values: deflate to month 0
    balance = deflate_value(float(row["balance"]), month, annual_inflation)
    investment = deflate_value(float(row["investment_values"]), month, annual_inflation)

    # Cumulative interest: sum of individually deflated monthly payments
    interest_rows = df.loc[df["month"] <= month, ["month", "interest"]]
    real_interest = sum(
        deflate_value(float(r["interest"]), int(r["month"]), annual_inflation)
        for _, r in interest_rows.iterrows()
    )

    # Cumulative tax savings: sum of individually deflated yearly savings
    interests_to_month = df.loc[df["month"] <= month, "interest"].tolist()
    taxes = Taxes(interests_to_month)
    yearly_savings = taxes.calculate_yearly_tax_savings()
    real_tax = sum(
        deflate_value(saving, (year_idx + 1) * 12, annual_inflation)
        for year_idx, saving in enumerate(yearly_savings)
    )

    return {
        "balance": balance,
        "investment": investment,
        "tax_cumulative": round(real_tax, 2),
        "interest_cumulative": round(real_interest, 2),
    }


def build_summary_dataframe(results: list[ScenarioResult]) -> pd.DataFrame:
    rows = []
    for result in results:
        row = {
            "Scénář": result.name,
            "Měsíční splátka": result.monthly_payment,
            "Měsíční úspora": result.monthly_savings,
            "Referenční splátka pro investici": result.reference_monthly_payment,
            "Délka hypotéky [roky]": result.loan_length_years,
            "Průměrná roční daňová úspora": result.average_yearly_tax_savings,
            "Měsíc plného doplacení investicí": result.payoff_month_with_investment,
        }
        rows.append(row)
    return pd.DataFrame(rows)


def _collect_milestone_months(non_baseline: list[ScenarioResult]) -> list[tuple[int, str]]:
    """Collect milestone months with labels: variant ends, payoff months, common horizon."""
    payoff_months = set()
    for r in non_baseline:
        if r.payoff_month_with_investment is not None:
            payoff_months.add(r.payoff_month_with_investment)

    variant_end_months = {r.variant_end_month for r in non_baseline}

    common_end = max((r.comparison_end_month for r in non_baseline), default=0) if non_baseline else 0

    all_months = set()
    all_months.update(variant_end_months)
    all_months.update(payoff_months)
    if common_end and common_end not in all_months:
        all_months.add(common_end)

    labeled = []
    for month in sorted(all_months):
        year = month // 12
        suffix = ""
        if month in payoff_months:
            suffix = " — možnost splacení"
        labeled.append((month, f"Měsíc {month} ({year}. rok){suffix}"))
    return labeled


def build_milestone_dataframes(results: list[ScenarioResult]) -> list[tuple[str, pd.DataFrame]]:
    """Build a list of (section_label, dataframe) for each milestone month."""
    non_baseline = [r for r in results if not r.is_baseline]
    milestones = _collect_milestone_months(non_baseline)

    milestone_dfs = []
    for month, label in milestones:
        rows = []
        for result in non_baseline:
            data = _extract_at_month(result, month)
            if data["balance"] is None:
                continue
            balance_net = round(data["investment"] + data["tax_cumulative"] - data["balance"], 2)
            profit_loss = round(data["investment"] + data["tax_cumulative"] - data["interest_cumulative"], 2)
            rows.append({
                "Scénář": result.name,
                "Zaplacené úroky": data["interest_cumulative"],
                "Zbývající dluh": data["balance"],
                "Investice": data["investment"],
                "Daňová úspora": data["tax_cumulative"],
                "Bilance": balance_net,
                "Zisk/ztráta": profit_loss,
            })
        if rows:
            milestone_dfs.append((label, pd.DataFrame(rows)))
    return milestone_dfs


def build_display_summary_dataframe(
    results: list[ScenarioResult],
    annual_inflation: float = 0.0,
    display_mode: str = "nominal",
) -> pd.DataFrame:
    summary_df = build_summary_dataframe(results)
    if display_mode != "real":
        return summary_df

    real_summary_df = summary_df.copy()
    real_summary_df["Měsíční splátka"] = [
        deflate_value(v, m, annual_inflation) for v, m in zip(real_summary_df["Měsíční splátka"], [r.monthly_payment_month for r in results])
    ]
    real_summary_df["Měsíční úspora"] = [
        deflate_value(v, m, annual_inflation) for v, m in zip(real_summary_df["Měsíční úspora"], [r.monthly_savings_month for r in results])
    ]
    real_summary_df["Referenční splátka pro investici"] = [
        deflate_value(v, m, annual_inflation) for v, m in zip(real_summary_df["Referenční splátka pro investici"], [r.monthly_savings_month for r in results])
    ]
    real_summary_df["Průměrná roční daňová úspora"] = [
        deflate_value(v, m, annual_inflation) for v, m in zip(real_summary_df["Průměrná roční daňová úspora"], [r.average_yearly_tax_savings_month for r in results])
    ]
    return real_summary_df


def build_display_milestone_dataframes(
    results: list[ScenarioResult],
    annual_inflation: float = 0.0,
    display_mode: str = "nominal",
) -> list[tuple[str, pd.DataFrame]]:
    if display_mode != "real" or annual_inflation <= 0:
        return build_milestone_dataframes(results)

    # In real mode, rebuild milestones with per-payment deflation
    non_baseline = [r for r in results if not r.is_baseline]
    milestones = _collect_milestone_months(non_baseline)

    milestone_dfs = []
    for month, label in milestones:
        rows = []
        for result in non_baseline:
            data = _extract_at_month(result, month, annual_inflation)
            if data["balance"] is None:
                continue
            balance_net = round(data["investment"] + data["tax_cumulative"] - data["balance"], 2)
            profit_loss = round(data["investment"] + data["tax_cumulative"] - data["interest_cumulative"], 2)
            rows.append({
                "Scénář": result.name,
                "Zaplacené úroky": data["interest_cumulative"],
                "Zbývající dluh": data["balance"],
                "Investice": data["investment"],
                "Daňová úspora": data["tax_cumulative"],
                "Bilance": balance_net,
                "Zisk/ztráta": profit_loss,
            })
        if rows:
            milestone_dfs.append((label, pd.DataFrame(rows)))
    return milestone_dfs
