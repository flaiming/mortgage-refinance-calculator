from modules.taxes import Taxes


def test_aggregate_yearly_interests():
    taxes = Taxes(interests_paid=[1000] * 24)

    interests_yearly = taxes.aggregate_yearly_interests()

    assert interests_yearly == [12000, 12000]


def test_yearly_deductible_interests_respect_limit():
    taxes = Taxes(interests_paid=[20000] * 12, yearly_interest_deduction_limit=150000)

    deductible_interests = taxes.calculate_yearly_deductible_interests()

    assert deductible_interests == [150000]


def test_yearly_tax_savings_are_fifteen_percent_of_deductible_interest():
    taxes = Taxes(interests_paid=[1000] * 24, yearly_interest_deduction_limit=150000, tax_rate=0.15)

    tax_savings = taxes.calculate_yearly_tax_savings()

    assert tax_savings == [1800.0, 1800.0]
    assert taxes.calculate_total_tax_savings() == 3600.0
