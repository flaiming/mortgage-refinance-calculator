from dataclasses import dataclass, field

import pandas as pd
from mortgage import Loan

from modules.loan_with_refinancing import LoanWithRefinancing
from modules.taxes import Taxes

# Remaining debt below this counts as paid off (balances are floats from Decimal schedules)
_EPSILON = 0.005


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
    # The common monthly budget (highest payment of all variants) every variant spends
    reference_monthly_payment: float | None = None
    is_baseline: bool = False
    extra_principal: float = 0.0
    refinancing_month: int = 0


# --- Time value helpers -------------------------------------------------------------

def monthly_inflation_rate(annual_inflation: float) -> float:
    return (1 + annual_inflation) ** (1 / 12) - 1


def monthly_return_rate(annual_return: float) -> float:
    """Monthly rate that compounds to the stated effective annual return."""
    return (1 + annual_return) ** (1 / 12) - 1


def deflate_value(value: float | None, month: int, annual_inflation: float) -> float | None:
    """Convert an amount paid or valued at the end of `month` to prices of month 0 (origination)."""
    if value is None or pd.isna(value):
        return None
    monthly_rate = monthly_inflation_rate(annual_inflation)
    return float(value) / ((1 + monthly_rate) ** max(month, 0))


def _accumulate_investments(contributions: list[float], monthly_rate: float) -> list[float]:
    """Portfolio value at each month end. A deposit made together with the month's mortgage
    payment starts earning from the next month; values keep full precision."""
    values = []
    value = 0.0
    for contribution in contributions:
        value = value * (1 + monthly_rate) + contribution
        values.append(value)
    return values


# --- Schedules ----------------------------------------------------------------------

def _schedule_rows(installments) -> list[dict]:
    return [
        {
            "month": int(part.number),
            "payment": float(part.payment),
            "interest": float(part.interest),
            "principal": float(part.principal),
            "total_interest": float(part.total_interest),
            "balance": max(0.0, float(part.balance)),
        }
        for part in installments
    ]


def _yearly_tax_savings(schedule_df: pd.DataFrame) -> list[float]:
    interests = schedule_df.loc[schedule_df["payment"] > 0, "interest"].tolist()
    return Taxes(interests).calculate_yearly_tax_savings()


def _tax_savings_cumulative(months, yearly_tax_savings: list[float]) -> list[float]:
    """Tax savings for a year are credited at its end, so only completed years count."""
    return [round(sum(yearly_tax_savings[: int(month) // 12]), 2) for month in months]


def _net_result(investment_value: float, contributions: float, tax_savings: float, interest: float) -> float:
    """Investment gain + tax savings - interest, i.e. minus the net cost of the mortgage.

    Only the gain on investments counts: the contributions themselves came out of the
    household budget, so counting their full value would reward a variant for money it
    merely moved from one pocket to another.
    """
    return round(investment_value - contributions + tax_savings - interest, 2)


def _tax_stats(yearly_tax_savings: list[float]) -> dict:
    if not yearly_tax_savings:
        return {
            "max_yearly_tax_savings": 0.0,
            "max_yearly_tax_savings_month": None,
            "average_yearly_tax_savings": 0.0,
            "average_yearly_tax_savings_month": None,
        }
    maximum = max(yearly_tax_savings)
    return {
        "max_yearly_tax_savings": maximum,
        "max_yearly_tax_savings_month": (yearly_tax_savings.index(maximum) + 1) * 12,
        "average_yearly_tax_savings": round(sum(yearly_tax_savings) / len(yearly_tax_savings), 2),
        "average_yearly_tax_savings_month": int(round(sum((i + 1) * 12 for i in range(len(yearly_tax_savings))) / len(yearly_tax_savings))),
    }


def _first_payoff_month(schedule_df: pd.DataFrame, after_month: int) -> int | None:
    rows = schedule_df[(schedule_df["month"] > after_month) & (schedule_df["balance"] > _EPSILON)]
    reached = rows[rows["investment_values"] >= rows["balance"]]
    if reached.empty:
        return None
    return int(reached["month"].iloc[0])


def build_baseline_result(principal: float, interest: float, term: int) -> ScenarioResult:
    loan = Loan(principal=principal, interest=interest, term=term)
    schedule = loan.schedule()[1:]
    # assign() instead of item assignment: pandas 2 on Python 3.14 raises false chained-assignment warnings
    schedule_df = pd.DataFrame(_schedule_rows(schedule)).assign(investment_values=0.0, investment_contribution=0.0)
    yearly_tax_savings = _yearly_tax_savings(schedule_df)
    schedule_df = schedule_df.assign(tax_savings_cumulative=_tax_savings_cumulative(schedule_df["month"], yearly_tax_savings))
    total_interest = float(schedule_df["interest"].sum())
    total_tax = round(sum(yearly_tax_savings), 2)
    end_month = int(schedule_df["month"].max())

    return ScenarioResult(
        name="Bez refinancování",
        initial_principal=float(principal),
        schedule_df=schedule_df,
        monthly_payment=float(schedule[0].payment),
        monthly_payment_month=1,
        monthly_savings=0.0,
        monthly_savings_month=1,
        total_interest=total_interest,
        loan_length_years=term,
        final_investment_value=0.0,
        payoff_month_with_investment=None,
        yearly_tax_savings=yearly_tax_savings,
        total_tax_savings=total_tax,
        tax_savings_at_variant_end=total_tax,
        investment_value_at_variant_end=0.0,
        net_result_at_variant_end=round(total_tax - total_interest, 2),
        net_result=round(total_tax - total_interest, 2),
        variant_end_month=end_month,
        comparison_end_month=end_month,
        reference_monthly_payment=None,
        is_baseline=True,
        **_tax_stats(yearly_tax_savings),
    )


@dataclass
class _VariantLoan:
    variant: RefinanceVariant
    schedule_df: pd.DataFrame
    monthly_payment: float


def _refinanced_loan(
    principal: float,
    original_interest: float,
    original_term: int,
    refinancing_year: int,
    variant: RefinanceVariant,
) -> _VariantLoan:
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
    return _VariantLoan(variant=variant, schedule_df=pd.DataFrame(_schedule_rows(schedule)), monthly_payment=float(loan.new_monthly_payment))


def _variant_result(
    loan: _VariantLoan,
    principal: float,
    refinancing_year: int,
    annual_return: float,
    monthly_budget: float,
    horizon_month: int,
    invest_after_payoff: bool,
) -> ScenarioResult:
    """Every variant spends the same `monthly_budget` after refinancing: its own mortgage
    payment plus investing whatever is left. Once its mortgage is paid off it invests the
    whole budget (when `invest_after_payoff`) until the common horizon."""
    refinancing_month = refinancing_year * 12
    schedule_df = loan.schedule_df.copy()
    variant_end_month = int(schedule_df["month"].max())

    if horizon_month > variant_end_month:
        last = schedule_df.iloc[-1]
        extension = pd.DataFrame(
            {
                "month": range(variant_end_month + 1, horizon_month + 1),
                "payment": 0.0,
                "interest": 0.0,
                "principal": 0.0,
                "total_interest": float(last["total_interest"]),
                "balance": 0.0,
            }
        )
        schedule_df = pd.concat([schedule_df, extension], ignore_index=True)

    contributions = []
    for month, payment in zip(schedule_df["month"], schedule_df["payment"]):
        if month <= refinancing_month:
            contributions.append(0.0)
        elif month <= variant_end_month:
            leftover = monthly_budget - float(payment)
            contributions.append(max(0.0, leftover))
        else:
            contributions.append(monthly_budget if invest_after_payoff else 0.0)

    schedule_df = schedule_df.assign(
        investment_contribution=contributions,
        investment_values=_accumulate_investments(contributions, monthly_return_rate(annual_return)),
    )
    yearly_tax_savings = _yearly_tax_savings(schedule_df)
    schedule_df = schedule_df.assign(tax_savings_cumulative=_tax_savings_cumulative(schedule_df["month"], yearly_tax_savings))

    monthly_savings = monthly_budget - loan.monthly_payment
    monthly_savings = max(0.0, monthly_savings)
    total_interest = float(schedule_df["interest"].sum())
    total_tax = round(sum(yearly_tax_savings), 2)

    at_end = schedule_df[schedule_df["month"] <= variant_end_month]
    investment_at_end = float(at_end["investment_values"].iloc[-1])

    return ScenarioResult(
        name=loan.variant.label(),
        initial_principal=float(principal),
        schedule_df=schedule_df,
        monthly_payment=loan.monthly_payment,
        monthly_payment_month=refinancing_month + 1,
        monthly_savings=monthly_savings,
        monthly_savings_month=refinancing_month + 1,
        total_interest=total_interest,
        loan_length_years=loan.variant.new_loan_length,
        final_investment_value=float(schedule_df["investment_values"].iloc[-1]),
        payoff_month_with_investment=_first_payoff_month(schedule_df, refinancing_month) if monthly_savings > 0 else None,
        yearly_tax_savings=yearly_tax_savings,
        total_tax_savings=total_tax,
        tax_savings_at_variant_end=total_tax,
        investment_value_at_variant_end=investment_at_end,
        net_result_at_variant_end=_net_result(investment_at_end, float(at_end["investment_contribution"].sum()), total_tax, total_interest),
        net_result=_net_result(
            float(schedule_df["investment_values"].iloc[-1]),
            float(schedule_df["investment_contribution"].sum()),
            total_tax,
            total_interest,
        ),
        variant_end_month=variant_end_month,
        comparison_end_month=max(horizon_month, variant_end_month),
        reference_monthly_payment=monthly_budget,
        is_baseline=False,
        extra_principal=float(loan.variant.extra_principal),
        refinancing_month=refinancing_month,
        **_tax_stats(yearly_tax_savings),
    )


def build_variant_result(
    principal: float,
    original_interest: float,
    original_term: int,
    refinancing_year: int,
    variant: RefinanceVariant,
    annual_return: float,
    monthly_budget: float | None = None,
) -> ScenarioResult:
    """A single variant on its own; without a budget it spends just its own payment."""
    loan = _refinanced_loan(principal, original_interest, original_term, refinancing_year, variant)
    return _variant_result(
        loan,
        principal,
        refinancing_year,
        annual_return,
        monthly_budget=loan.monthly_payment if monthly_budget is None else monthly_budget,
        horizon_month=int(loan.schedule_df["month"].max()),
        invest_after_payoff=False,
    )


def build_variant_results(
    principal: float,
    original_interest: float,
    original_term: int,
    refinancing_year: int,
    variants: list[RefinanceVariant],
    annual_return: float,
    invest_after_payoff: bool = True,
) -> list[ScenarioResult]:
    """Compare variants with one common monthly budget, the highest new payment among them.

    Each variant pays its mortgage and invests the rest of the budget; after payoff it invests
    the whole budget. All variants therefore spend the same every month until the common
    horizon (the end of the longest variant), and differ only in what they own at the end.
    The result does not depend on the order or grouping of the variants.
    """
    loans = [_refinanced_loan(principal, original_interest, original_term, refinancing_year, v) for v in variants]
    if not loans:
        return []
    monthly_budget = max(loan.monthly_payment for loan in loans)
    horizon_month = max(int(loan.schedule_df["month"].max()) for loan in loans)

    results = [
        _variant_result(loan, principal, refinancing_year, annual_return, monthly_budget, horizon_month, invest_after_payoff)
        for loan in loans
    ]
    sorted_results = sorted(results, key=lambda result: (result.loan_length_years, result.name))

    # Deduplicate names by appending a counter suffix
    name_counts: dict[str, int] = {}
    for result in sorted_results:
        name_counts[result.name] = name_counts.get(result.name, 0) + 1
    seen: dict[str, int] = {}
    for result in sorted_results:
        base_name = result.name
        seen[base_name] = seen.get(base_name, 0) + 1
        if name_counts[base_name] > 1:
            result.name = f"{base_name} ({seen[base_name]})"

    return sorted_results


# --- Display tables -----------------------------------------------------------------

def build_graph_dataframe(results: list[ScenarioResult], refinancing_year: int | None = None) -> pd.DataFrame:
    graph_data: dict[str, pd.Series] = {}
    refinancing_cutoff_month = None if refinancing_year is None else refinancing_year * 12
    for result in results:
        schedule_df = result.schedule_df.set_index("month")
        balance_series = schedule_df["balance"]
        if result.is_baseline and refinancing_cutoff_month is not None:
            balance_series = balance_series.where(balance_series.index <= refinancing_cutoff_month)
        balance_series = balance_series.where(balance_series > 0)
        graph_data[f"{result.name} - zůstatek"] = balance_series
        if not result.is_baseline and schedule_df["investment_values"].max() > 0:
            inv_series = schedule_df["investment_values"]
            graph_data[f"{result.name} - investice"] = inv_series.where(inv_series > 0)

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

    factors = _deflators(graph_df.index, annual_inflation)
    return graph_df.mul(factors, axis=0)


def _deflators(months, annual_inflation: float) -> pd.Series:
    monthly_rate = monthly_inflation_rate(annual_inflation)
    months = pd.Series(months, index=months, dtype=float)
    return (1 + monthly_rate) ** -months.clip(lower=0)


INFLATION_RELIEF_COLUMN = "Inflační úleva na jistině"


def _extract_at_month(result: ScenarioResult, month: int, annual_inflation: float = 0.0) -> dict | None:
    """Metrics of one variant at the end of `month`.

    With inflation, every flow is converted to month-0 prices at the month it happens. Repaying
    principal later in cheaper money is then a real gain, reported as "inflation relief": the
    borrowed amount minus the real value of principal repaid so far and of the remaining debt.
    In nominal terms it is always zero.
    """
    df = result.schedule_df
    upto = df[df["month"] <= month]
    if upto.empty or int(upto["month"].iloc[-1]) != month:
        return None
    row = upto.iloc[-1]
    completed_years = min(month // 12, len(result.yearly_tax_savings))

    if annual_inflation <= 0:
        return {
            "balance": float(row["balance"]),
            "investment": float(row["investment_values"]),
            "tax_cumulative": round(sum(result.yearly_tax_savings[:completed_years]), 2),
            "interest_cumulative": float(upto["interest"].sum()),
            "contributions_cumulative": float(upto["investment_contribution"].sum()),
            "inflation_relief": 0.0,
        }

    factors = _deflators(upto["month"].to_numpy(), annual_inflation).to_numpy()
    month_factor = float(_deflators([month], annual_inflation).iloc[0])
    real_tax = sum(
        saving * float(_deflators([(year + 1) * 12], annual_inflation).iloc[0])
        for year, saving in enumerate(result.yearly_tax_savings[:completed_years])
    )
    borrowed = result.initial_principal + result.extra_principal * float(
        _deflators([result.refinancing_month], annual_inflation).iloc[0]
    )
    principal_repaid = float((upto["principal"].to_numpy() * factors).sum())
    balance = float(row["balance"]) * month_factor

    return {
        "balance": balance,
        "investment": float(row["investment_values"]) * month_factor,
        "tax_cumulative": round(real_tax, 2),
        "interest_cumulative": float((upto["interest"].to_numpy() * factors).sum()),
        "contributions_cumulative": float((upto["investment_contribution"].to_numpy() * factors).sum()),
        "inflation_relief": borrowed - principal_repaid - balance,
    }


def build_summary_dataframe(results: list[ScenarioResult]) -> pd.DataFrame:
    rows = []
    for result in results:
        rows.append(
            {
                "Scénář": result.name,
                "Měsíční splátka": result.monthly_payment,
                "Měsíční rozpočet": result.reference_monthly_payment,
                "Měsíčně investováno": result.monthly_savings,
                "Délka hypotéky [roky]": result.loan_length_years,
                "Průměrná roční daňová úspora": result.average_yearly_tax_savings,
                "Měsíc plného doplacení investicí": result.payoff_month_with_investment,
            }
        )
    return pd.DataFrame(rows)


def build_display_summary_dataframe(
    results: list[ScenarioResult],
    annual_inflation: float = 0.0,
    display_mode: str = "nominal",
) -> pd.DataFrame:
    summary_df = build_summary_dataframe(results)
    if display_mode != "real":
        return summary_df

    real_summary_df = summary_df.copy()
    for column in ["Měsíční splátka", "Měsíční rozpočet", "Měsíčně investováno"]:
        real_summary_df[column] = [
            deflate_value(value, result.monthly_payment_month, annual_inflation)
            for value, result in zip(real_summary_df[column], results)
        ]
    # Each yearly refund is deflated at the end of its own year, then averaged
    real_summary_df["Průměrná roční daňová úspora"] = [
        round(
            sum(deflate_value(saving, (year + 1) * 12, annual_inflation) for year, saving in enumerate(result.yearly_tax_savings))
            / len(result.yearly_tax_savings),
            2,
        )
        if result.yearly_tax_savings
        else 0.0
        for result in results
    ]
    return real_summary_df


def _collect_milestone_months(non_baseline: list[ScenarioResult]) -> list[tuple[int, str]]:
    """Collect milestone months with labels: variant ends, payoff months, common horizon."""
    payoff_months = {r.payoff_month_with_investment for r in non_baseline if r.payoff_month_with_investment is not None}
    all_months = {r.variant_end_month for r in non_baseline} | payoff_months
    common_end = max((r.comparison_end_month for r in non_baseline), default=0)
    if common_end:
        all_months.add(common_end)

    labeled = []
    for month in sorted(all_months):
        suffix = " — možnost splacení" if month in payoff_months else ""
        labeled.append((month, f"Měsíc {month} ({month // 12}. rok){suffix}"))
    return labeled


def _milestone_dataframes(results: list[ScenarioResult], annual_inflation: float = 0.0) -> list[tuple[str, pd.DataFrame]]:
    non_baseline = [r for r in results if not r.is_baseline]
    milestone_dfs = []
    for month, label in _collect_milestone_months(non_baseline):
        rows = []
        for result in non_baseline:
            data = _extract_at_month(result, month, annual_inflation)
            if data is None:
                continue
            investment_gain = data["investment"] - data["contributions_cumulative"]
            net_cost = data["interest_cumulative"] - data["tax_cumulative"] - investment_gain - data["inflation_relief"]
            row = {
                "Scénář": result.name,
                "Zaplacené úroky": data["interest_cumulative"],
                "Daňová úspora": data["tax_cumulative"],
            }
            if annual_inflation > 0:
                row[INFLATION_RELIEF_COLUMN] = data["inflation_relief"]
            row.update(
                {
                    "Vloženo do investic": data["contributions_cumulative"],
                    "Hodnota investic": data["investment"],
                    "Zbývající dluh": data["balance"],
                    "Čisté náklady": net_cost,
                }
            )
            rows.append(row)
        if rows:
            milestone_dfs.append((label, pd.DataFrame(rows)))
    return milestone_dfs


def build_milestone_dataframes(results: list[ScenarioResult]) -> list[tuple[str, pd.DataFrame]]:
    """Build a list of (section_label, dataframe) for each milestone month.

    "Čisté náklady" = interest paid - tax savings - investment gain (value minus own
    contributions). Lower is better; it is the metric variants are ranked by. With the
    common monthly budget, a lower net cost means more money at the horizon.
    """
    return _milestone_dataframes(results)


def build_display_milestone_dataframes(
    results: list[ScenarioResult],
    annual_inflation: float = 0.0,
    display_mode: str = "nominal",
) -> list[tuple[str, pd.DataFrame]]:
    if display_mode != "real" or annual_inflation <= 0:
        return build_milestone_dataframes(results)
    return _milestone_dataframes(results, annual_inflation)


def best_scenario(milestone_df: pd.DataFrame) -> str | None:
    """Scenario with the lowest net cost, compared on unrounded values."""
    if milestone_df.empty:
        return None
    return str(milestone_df.loc[milestone_df["Čisté náklady"].idxmin(), "Scénář"])
