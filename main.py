import json
import plotly.graph_objects as go
import streamlit as st
import pandas as pd

from comparison import (
    RefinanceVariant,
    build_baseline_result,
    build_display_graph_dataframe,
    build_display_milestone_dataframes,
    build_display_net_balance_graph_dataframe,
    build_display_summary_dataframe,
    build_variant_results,
)
from investing_strategies import FIXED_INTEREST_RATES

RISK_OPTIONS = {
    "safe": "Konzervativní",
    "medium": "Vyvážená",
    "risky": "Dynamická",
    "custom": "Vlastní",
}


def risk_option_label(risk_key: str) -> str:
    if risk_key == "custom":
        return "Vlastní"
    return f"{RISK_OPTIONS[risk_key]} ({FIXED_INTEREST_RATES[risk_key] * 100:.0f} % ročně)"


def _format_czk(value: float) -> str:
    return f"{int(round(value)):,}".replace(",", " ")


VARIANT_COLORS = [
    "#1f77b4",  # modrá
    "#d62728",  # červená
    "#2ca02c",  # zelená
    "#ff7f0e",  # oranžová
    "#9467bd",  # fialová
    "#8c564b",  # hnědá
]

LINE_STYLES = {
    "zůstatek": "solid",
    "investice": "dash",
    "daňová úspora": "dot",
}


def render_line_chart(graph_df: pd.DataFrame, y_label: str = "Kč", markers: list[dict] | None = None):
    fig = go.Figure()

    # Assign a color per variant name
    variant_names = []
    for column in graph_df.columns:
        if " - " in column:
            variant_name = column.rsplit(" - ", 1)[0]
        else:
            variant_name = column
        if variant_name not in variant_names:
            variant_names.append(variant_name)
    color_map = {name: VARIANT_COLORS[i % len(VARIANT_COLORS)] for i, name in enumerate(variant_names)}

    for column in graph_df.columns:
        series = graph_df[column].dropna()
        if " - " in column:
            variant_name, line_type = column.rsplit(" - ", 1)
        else:
            variant_name, line_type = column, ""
        color = color_map.get(variant_name, "#333333")
        dash = LINE_STYLES.get(line_type, "solid")
        fig.add_trace(go.Scatter(
            x=series.index,
            y=series.values,
            mode="lines",
            name=column,
            line=dict(color=color, dash=dash, width=2),
            hovertemplate="%{x} m<br>%{customdata}<extra>%{fullData.name}</extra>",
            customdata=[_format_czk(v) + " Kč" for v in series.values],
        ))

    max_month = int(graph_df.index.max())
    tick_vals = list(range(12, max_month + 1, 12))
    tick_text = [f"{m} ({m // 12}. rok)" for m in tick_vals]

    fig.update_layout(
        xaxis=dict(
            title="Měsíce",
            tickvals=tick_vals,
            ticktext=tick_text,
            tickangle=-45,
        ),
        yaxis=dict(
            title=y_label,
            tickformat=",.0f",
            separatethousands=True,
        ),
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
    )

    # Plotly uses comma by default — replace with spaces for CZK formatting
    fig.update_layout(separators=", ")

    if markers:
        for m in markers:
            color = color_map.get(m.get("variant", ""), "#333333")
            fig.add_trace(go.Scatter(
                x=[m["x"]],
                y=[m["y"]],
                mode="markers+text",
                marker=dict(size=12, color=color, symbol="diamond", line=dict(width=2, color="white")),
                text=[m.get("label", "")],
                textposition="top center",
                textfont=dict(size=11),
                showlegend=False,
                hovertemplate=f"{m.get('label', '')}<br>{m['x']} m<br>{_format_czk(m['y'])} Kč<extra></extra>",
            ))

    st.plotly_chart(fig, use_container_width=True)


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


def ensure_variant_state():
    if "refinance_variants" not in st.session_state:
        url_variants = _qp_variants()
        if url_variants:
            st.session_state.refinance_variants = url_variants
        else:
            st.session_state.refinance_variants = [
                {
                    "id": 1,
                    "refinancing_interest": 5.0,
                    "length_change": 0,
                    "extra_principal": 0,
                },
                {
                    "id": 2,
                    "refinancing_interest": 5.0,
                    "length_change": 7,
                    "extra_principal": 0,
                }
            ]
    if "next_variant_id" not in st.session_state:
        st.session_state.next_variant_id = max((variant["id"] for variant in st.session_state.refinance_variants), default=0) + 1

    sanitized_variants = []
    for variant in st.session_state.refinance_variants:
        sanitized_variants.append(
            {
                "id": variant["id"],
                "refinancing_interest": float(variant["refinancing_interest"]),
                "length_change": int(variant["length_change"]),
                "extra_principal": int(variant.get("extra_principal", 0)),
            }
        )
    st.session_state.refinance_variants = sanitized_variants


def add_variant():
    new_id = st.session_state.next_variant_id
    st.session_state.next_variant_id += 1
    st.session_state.refinance_variants.append(
        {
            "id": new_id,
            "refinancing_interest": 5.0,
            "length_change": 0,
            "extra_principal": 0,
        }
    )
    st.rerun()


def remove_variant(variant_id: int):
    st.session_state.refinance_variants = [
        variant for variant in st.session_state.refinance_variants if variant["id"] != variant_id
    ]
    st.rerun()


def _qp_int(key: str, default: int) -> int:
    try:
        return int(st.query_params.get(key, default))
    except (ValueError, TypeError):
        return default


def _qp_float(key: str, default: float) -> float:
    try:
        return float(st.query_params.get(key, default))
    except (ValueError, TypeError):
        return default


def _qp_str(key: str, default: str) -> str:
    return st.query_params.get(key, default)


def _qp_variants() -> list[dict] | None:
    raw = st.query_params.get("variants")
    if not raw:
        return None
    try:
        parsed = json.loads(raw)
        if not isinstance(parsed, list):
            return None
        variants = []
        for i, v in enumerate(parsed):
            variants.append({
                "id": i + 1,
                "refinancing_interest": float(v.get("rate", 5.0)),
                "length_change": int(v.get("years", 0)),
                "extra_principal": int(v.get("extra", 0)),
            })
        return variants if variants else None
    except (json.JSONDecodeError, TypeError):
        return None


st.set_page_config(layout="wide")
st.markdown(
    "<style>.block-container { max-width: 67.5rem !important; margin: 0 auto; }</style>",
    unsafe_allow_html=True,
)
st.title("Kalkulačka refinancování hypotéky")

with st.container(border=True):
    st.markdown("**Původní hypotéka**")
    col1, col2, col3, col4 = st.columns(4)
    home_value = col1.number_input("Splácená částka", min_value=0, value=_qp_int("principal", 2_500_000))
    old_loan_length = col2.number_input("Délka splácení [roky]", min_value=2, value=_qp_int("term", 30))
    old_interest_rate = col3.number_input("Úrok [%]", min_value=0.1, value=_qp_float("rate", 1.69)) / 100
    refinancing_year_options = list(range(1, old_loan_length))
    _qp_refi = _qp_int("refi_year", 7)
    _refi_index = refinancing_year_options.index(_qp_refi) if _qp_refi in refinancing_year_options else min(6, old_loan_length - 2)
    refinancing_year = col4.selectbox(
        "Rok refinancování",
        options=refinancing_year_options,
        index=_refi_index,
        format_func=lambda y: f"{y}.",
    )

with st.container(border=True):
    st.markdown("**Investiční strategie**")
    _qp_strategy = _qp_str("strategy", "medium")
    _strategy_keys = list(RISK_OPTIONS.keys())
    _strategy_index = _strategy_keys.index(_qp_strategy) if _qp_strategy in _strategy_keys else 1
    strategy_col, custom_rate_col = st.columns([2, 1])
    with strategy_col:
        risk_choice_label = st.selectbox(
            "Strategie",
            [risk_option_label(risk_key) for risk_key in RISK_OPTIONS],
            index=_strategy_index,
        )
        risk_choice = next(risk_key for risk_key in RISK_OPTIONS if risk_option_label(risk_key) == risk_choice_label)
    with custom_rate_col:
        custom_rate = st.number_input(
            "Roční výnos [%]",
            min_value=0.0,
            value=_qp_float("custom_rate", 6.0),
            step=0.5,
            disabled=risk_choice != "custom",
        )
    if risk_choice == "custom":
        FIXED_INTEREST_RATES["custom"] = custom_rate / 100

with st.container(border=True):
    st.markdown("**Zobrazení hodnot**")
    _qp_mode = _qp_str("mode", "nominal")
    mode_col, inflation_col = st.columns([1, 1])
    with mode_col:
        display_mode_label = st.segmented_control(
            "Režim",
            options=["Nominálně", "Reálně"],
            default="Reálně" if _qp_mode == "real" else "Nominálně",
        )
        display_mode = "real" if display_mode_label == "Reálně" else "nominal"
    with inflation_col:
        inflation = st.number_input("Roční inflace [%]", min_value=0.0, value=_qp_float("inflation", 2.0), disabled=display_mode != "real") / 100
    st.caption("Reálné hodnoty jsou přepočítané na dnešní kupní sílu. Daňový odpočet: limit 150 000 Kč/rok, sazba 15 %.")

ensure_variant_state()

st.subheader("Varianty refinancování")
st.caption("U každé varianty zadejte nový úrok a změnu délky hypotéky (+ prodloužení, − zkrácení). Rok refinancování je společný pro všechny varianty.")

if st.button("Přidat variantu"):
    add_variant()

updated_variants = []
for variant in st.session_state.refinance_variants:
    variant_id = variant["id"]
    rate_key = f"refinancing_interest_{variant_id}"
    change_key = f"length_change_{variant_id}"
    extra_key = f"extra_principal_{variant_id}"

    st.session_state.setdefault(rate_key, variant["refinancing_interest"])
    st.session_state[rate_key] = float(st.session_state[rate_key])

    min_change = int(refinancing_year) + 1 - old_loan_length
    st.session_state.setdefault(change_key, variant["length_change"])
    st.session_state[change_key] = max(int(st.session_state[change_key]), min_change)

    st.session_state.setdefault(extra_key, variant["extra_principal"])

    with st.container(border=True):
        header_col, remove_col = st.columns([5, 1])
        header_col.markdown(f"**Varianta {variant_id}**")
        if remove_col.button("Smazat", key=f"remove_variant_{variant_id}"):
            remove_variant(variant_id)

        input_col1, input_col2, input_col3 = st.columns(3)
        refinancing_interest_pct = input_col1.number_input(
            "Nový úrok [%]",
            min_value=0.1,
            key=rate_key,
        )
        if st.session_state[change_key] < min_change:
            st.session_state[change_key] = min_change
        length_change = input_col2.number_input(
            "Přidání/odebrání let k původní délce",
            min_value=min_change,
            value=int(st.session_state[change_key]),
            key=change_key,
        )
        extra_principal = input_col3.number_input(
            "Navýšení hypotéky [Kč]",
            min_value=0,
            value=int(st.session_state[extra_key]),
            step=50_000,
            key=extra_key,
        )
        new_loan_length = old_loan_length + int(length_change)

        generated_label = RefinanceVariant(
            refinancing_interest=float(refinancing_interest_pct) / 100,
            new_loan_length=new_loan_length,
            extra_principal=float(extra_principal),
        ).label()
        st.caption(f"Celková délka: {new_loan_length} let — {generated_label}")

        updated_variants.append(
            {
                "id": variant_id,
                "refinancing_interest": float(refinancing_interest_pct),
                "length_change": int(length_change),
                "extra_principal": int(extra_principal),
            }
        )

st.session_state.refinance_variants = updated_variants

# Sync all inputs to URL query params (only if changed, to avoid extra reruns)
_variants_json = json.dumps(
    [{"rate": v["refinancing_interest"], "years": v["length_change"], "extra": v["extra_principal"]}
     for v in updated_variants],
    separators=(",", ":"),
)
_new_params = {
    "principal": str(home_value),
    "term": str(old_loan_length),
    "rate": str(round(old_interest_rate * 100, 4)),
    "refi_year": str(refinancing_year),
    "strategy": risk_choice,
    "custom_rate": str(custom_rate),
    "mode": display_mode,
    "inflation": str(round(inflation * 100, 4)),
    "variants": _variants_json,
}
if {k: st.query_params.get(k) for k in _new_params} != _new_params:
    st.query_params.update(_new_params)

results = [build_baseline_result(home_value, old_interest_rate, old_loan_length)]
variant_errors = []
variant_configs = []
for variant in st.session_state.refinance_variants:
    variant_configs.append(
        RefinanceVariant(
            refinancing_interest=variant["refinancing_interest"] / 100,
            new_loan_length=old_loan_length + variant["length_change"],
            extra_principal=float(variant["extra_principal"]),
        )
    )

try:
    results.extend(
        build_variant_results(
            principal=home_value,
            original_interest=old_interest_rate,
            original_term=old_loan_length,
            refinancing_year=int(refinancing_year),
            variants=variant_configs,
            risk_choice=risk_choice,
        )
    )
except ValueError as exc:
    variant_errors.append(str(exc))

for error in variant_errors:
    st.error(error)

st.subheader("Porovnání scénářů")
graph_df = build_display_graph_dataframe(
    results,
    refinancing_year=int(refinancing_year),
    annual_inflation=inflation,
    display_mode=display_mode,
)
# Find investment-crosses-balance markers
payoff_markers = []
for result in results:
    if result.is_baseline or result.payoff_month_with_investment is None:
        continue
    month = result.payoff_month_with_investment
    row = result.schedule_df.loc[result.schedule_df["month"] == month]
    if not row.empty:
        value = float(row.iloc[0]["investment_values"])
        payoff_markers.append({
            "x": month,
            "y": value,
            "variant": result.name,
            "label": f"Splacení ({month}. m)",
        })
render_line_chart(graph_df, markers=payoff_markers)

st.subheader("Aktuální bilance prostředků")
st.caption("Bilance = investice + kumulativní daňová úspora - zbývající dluh. Na začátku tedy začíná v mínusu ve výši celé hypotéky.")
net_balance_graph_df = build_display_net_balance_graph_dataframe(
    results,
    refinancing_year=int(refinancing_year),
    annual_inflation=inflation,
    display_mode=display_mode,
)
# Find balance-crosses-zero markers
zero_cross_markers = []
for result in results:
    if result.is_baseline:
        continue
    df = result.schedule_df
    net = df["investment_values"] + df["tax_savings_cumulative"] - df["balance"]
    crossed = df.loc[net >= 0, "month"]
    if not crossed.empty:
        month = int(crossed.iloc[0])
        net_val = float(net.loc[df["month"] == month].iloc[0])
        zero_cross_markers.append({
            "x": month,
            "y": net_val,
            "variant": result.name,
            "label": f"Bilance ≥ 0 ({month}. m)",
        })
render_line_chart(net_balance_graph_df, markers=zero_cross_markers)

summary_df = build_display_summary_dataframe(
    results,
    annual_inflation=inflation,
    display_mode=display_mode,
)
milestone_dfs = build_display_milestone_dataframes(
    results,
    annual_inflation=inflation,
    display_mode=display_mode,
)
ranked_variants_df = rank_refinance_variants(summary_df, milestone_dfs)

# Determine recommended scenario
recommended_scenario = None
if not ranked_variants_df.empty:
    rec_rows = ranked_variants_df[ranked_variants_df["Doporučeno"] == True]
    if not rec_rows.empty:
        recommended_scenario = rec_rows.iloc[0]["Scénář"]

if len(ranked_variants_df) >= 2 and milestone_dfs:
    best_variant = ranked_variants_df.iloc[0]
    last_milestone_label, last_milestone_df = milestone_dfs[-1]
    best_in_last = last_milestone_df[last_milestone_df["Scénář"] == best_variant["Scénář"]]
    st.subheader("Doporučení")
    if not best_in_last.empty:
        best_data = best_in_last.iloc[0]
        recommendation_text = (
            f"Nejvýhodnější varianta je **{best_variant['Scénář']}** "
            f"se ziskem/ztrátou {format_currency(best_data['Zisk/ztráta'])} na konci horizontu ({last_milestone_label}). "
            "Porovnání je počítané ve stejném horizontu jako nejdelší zadaná varianta; "
            "kratší varianta po splacení hypotéky dál investuje svou bývalou měsíční splátku."
        )
        if pd.notna(best_variant["Měsíc plného doplacení investicí"]):
            recommendation_text += f" Investice dorovná hypotéku v měsíci {int(best_variant['Měsíc plného doplacení investicí'])}."
        st.write(recommendation_text)

st.subheader("Souhrn variant")
formatted_df = format_summary_dataframe(summary_df)
transposed_df = formatted_df.set_index("Scénář").T
transposed_df.index.name = None
st.table(transposed_df)

# Milestone comparison tables
st.caption("**Bilance** = investice + daňová úspora − zbývající dluh (kolik čistého majetku mám v daném okamžiku)")
st.caption("**Zisk/ztráta** = investice + daňová úspora − celkový zaplacený úrok (celkový profit/ztráta z refinancování)")
for label, milestone_df in milestone_dfs:
    st.subheader(label)
    best_at_milestone = milestone_df.loc[milestone_df["Zisk/ztráta"].idxmax(), "Scénář"] if not milestone_df.empty else None
    formatted_milestone = format_milestone_dataframe(milestone_df)
    transposed_milestone = formatted_milestone.set_index("Scénář").T
    transposed_milestone.index.name = None
    milestone_styled = transposed_milestone.style
    if best_at_milestone and best_at_milestone in transposed_milestone.columns:
        milestone_styled = milestone_styled.set_properties(
            subset=[best_at_milestone],
            **{"background-color": "#d4edda", "font-weight": "bold"},
        )
    st.table(milestone_styled)

if summary_df["Měsíční úspora"].max() <= 0:
    st.info("Žádná z delších variant momentálně nevytváří úsporu vůči své referenční refinanční variantě, takže investiční křivka zůstává na nule.")
