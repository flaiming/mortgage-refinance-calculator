from decimal import Decimal

from loan_with_refinancing import LoanWithRefinancing


def test_loan_with_refinancing():
    hypo_total = 100_000
    p_a = 0.01
    years = 2
    refinancing_year = 1
    refinancing_p_a = 0.1
    length_change = 0

    loan = LoanWithRefinancing(
        principal=hypo_total,
        interest=p_a,
        term=years,
        refinancing_year=refinancing_year,
        refinancing_interest=refinancing_p_a,
        new_hypo_length_change_years=length_change,
    )

    total_interest = 0
    total_principal = 0

    schedule = loan.schedule_with_refinancing()
    assert len(schedule) == 24
    for part in schedule:
        total_interest += part.interest
        total_principal += part.principal

    assert int(total_principal) == Decimal(100_000.0)
    assert total_interest == Decimal("3535.664373251231795866491537")


def test_length_change():
    hypo_total = 100_000
    p_a = 0.01
    years = 2
    refinancing_year = 1
    refinancing_p_a = 0.1
    length_change = 1

    loan = LoanWithRefinancing(
        principal=hypo_total,
        interest=p_a,
        term=years,
        refinancing_year=refinancing_year,
        refinancing_interest=refinancing_p_a,
        new_hypo_length_change_years=length_change,
    )

    total_interest = 0
    total_principal = 0

    schedule = loan.schedule_with_refinancing()
    assert len(schedule) == 12 * 3
    for part in schedule:
        total_interest += part.interest
        total_principal += part.principal

    assert int(total_principal) == Decimal(100_000.0)
    assert total_interest == Decimal("6173.159962967634185913480474")


def test_schedule_numbers_continue_after_refinancing():
    loan = LoanWithRefinancing(
        principal=100_000,
        interest=0.01,
        term=2,
        refinancing_year=1,
        refinancing_interest=0.10,
        new_hypo_length_change_years=1,
    )

    schedule = loan.schedule_with_refinancing()

    assert schedule[0].number == 1
    assert schedule[-1].number == 36
    assert [part.number for part in schedule] == list(range(1, 37))


def test_investment_stays_zero_when_refinancing_does_not_save_money():
    loan = LoanWithRefinancing(
        principal=2_500_000,
        interest=0.0169,
        term=30,
        refinancing_year=7,
        refinancing_interest=0.05,
        new_hypo_length_change_years=0,
    )

    schedule = loan.schedule_with_refinancing()

    assert loan.monthly_payment_difference_after_refinancing == 0
    assert all(part.monthly_payment_difference == 0 for part in schedule if part.number > 12 * 7)
    assert all(part.investment_values.get("risky", 0) == 0 for part in schedule if part.number > 12 * 7)
