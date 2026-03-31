import math

import pandas as pd

from main import format_summary_dataframe, rank_refinance_variants


def test_format_summary_dataframe_handles_nan_currency_values():
    summary_df = pd.DataFrame(
        [
            {
                "Scénář": "Bez refinancování",
                "Měsíční splátka": 10000.0,
                "Měsíční úspora": 0.0,
                "Referenční splátka pro investici": math.nan,
                "Délka hypotéky [roky]": 30,
                "Průměrná roční daňová úspora": 5000.0,
                "Měsíc plného doplacení investicí": math.nan,
            }
        ]
    )

    formatted_df = format_summary_dataframe(summary_df)

    assert formatted_df.loc[0, "Referenční splátka pro investici"] == "-"
    assert formatted_df.loc[0, "Měsíční splátka"] == "10 000 Kč"
    assert formatted_df.loc[0, "Měsíc plného doplacení investicí"] == "Nedosaženo"


def test_rank_refinance_variants_ignores_baseline_and_assigns_order():
    summary_df = pd.DataFrame(
        [
            {
                "Scénář": "Bez refinancování",
                "Měsíc plného doplacení investicí": math.nan,
            },
            {
                "Scénář": "5.00 % | 30 let",
                "Měsíc plného doplacení investicí": math.nan,
            },
            {
                "Scénář": "5.00 % | 37 let",
                "Měsíc plného doplacení investicí": 310.0,
            },
        ]
    )
    milestone_dfs = [
        (
            "Měsíc 444 (37. rok)",
            pd.DataFrame(
                [
                    {"Scénář": "5.00 % | 30 let", "Zisk/ztráta": -70000.0, "Investice": 100000.0},
                    {"Scénář": "5.00 % | 37 let", "Zisk/ztráta": 65000.0, "Investice": 250000.0},
                ]
            ),
        )
    ]

    ranked_df = rank_refinance_variants(summary_df, milestone_dfs)

    assert list(ranked_df["Scénář"]) == ["5.00 % | 37 let", "5.00 % | 30 let"]
    assert list(ranked_df["Pořadí"]) == [1, 2]
    assert bool(ranked_df.loc[0, "Doporučeno"]) is True
    assert bool(ranked_df.loc[1, "Doporučeno"]) is False
