from investor import Investor, InvestmentData


def init_investor():
    invest_data = InvestmentData()
    monthly_invest = 1000
    yearly_interest_rates = {
        "risky": 0.08,
        "medium": 0.05,
        "safe": 0.03,
    }

    investor = Investor(
        invest_data=invest_data,
        monthly_invest=monthly_invest,
        yearly_interest_rates=yearly_interest_rates
    )
    return investor, invest_data


def test_calculate_investments():
    investor, invest_data = init_investor()
    for i in range(12):
        investor.add_investment(1000)

    assert invest_data.risky_values[2] == 3040
    assert invest_data.medium_values[2] == 3025
    assert invest_data.safe_values[2] == 3015
