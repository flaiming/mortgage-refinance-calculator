from dataclasses import dataclass, field
from investing_strategies import FIXED_INTEREST_RATES, InvestStrategies


@dataclass
class InvestmentData:
    risky_values: list = field(default_factory=list)
    medium_values: list = field(default_factory=list)
    safe_values: list = field(default_factory=list)


class Investor:

    def __init__(
        self,
        invest_data: InvestmentData,
        monthly_invest: float,
        yearly_interest_rates: dict = None,
    ):
        self.invest_data = invest_data
        self.monthly_invest = monthly_invest
        self.yearly_interest_rates = self.get_interest_rates() if not yearly_interest_rates else yearly_interest_rates
        self.curr_val_risky = 0
        self.curr_val_medium = 0
        self.curr_val_safe = 0
        self.risky_reached = False
        self.medium_reached = False
        self.safe_reached = False

    @staticmethod
    def get_interest_rates():
        return dict(FIXED_INTEREST_RATES)

    def apply_interests(self):
        """
        Applies monthly interest rate to value of portfolios.
        Saves values to invest_data dataclass.
        """
        monthly_interest_multi = 1 + (self.yearly_interest_rates["risky"] / 12)
        self.curr_val_risky = self.curr_val_risky * monthly_interest_multi
        self.invest_data.risky_values.append(int(self.curr_val_risky))

        monthly_interest_multi = 1 + (self.yearly_interest_rates["medium"] / 12)
        self.curr_val_medium = self.curr_val_medium * monthly_interest_multi
        self.invest_data.medium_values.append(int(self.curr_val_medium))

        monthly_interest_multi = 1 + (self.yearly_interest_rates["safe"] / 12)
        self.curr_val_safe = self.curr_val_safe * monthly_interest_multi
        self.invest_data.safe_values.append(int(self.curr_val_safe))

    def add_investment(self, investment: float = None):
        """
        Adds monthly investment to risky, medium and safe portfolios
        and applies interest.
        investment: float containing investment to be added
        """
        monthly_invest = self.monthly_invest if not investment else investment
        self.curr_val_risky += monthly_invest
        self.curr_val_medium += monthly_invest
        self.curr_val_safe += monthly_invest
        self.apply_interests()
        return (self.invest_data.risky_values[-1], self.invest_data.medium_values[-1], self.invest_data.safe_values[-1])


if __name__ == "__main__":
    invest_data = InvestmentData()
    investor = Investor(
        invest_data=invest_data,
        monthly_invest=1000,
    )

    # yearly_interest_rates={
    #     "risky": 0.08, # add couple % to S&P?
    #     "medium": 0.05, # take from S&P index
    #     "safe": 0.03, # state bonds
    # },
    # for i in range(36):
    #     investor.add_investment(1000)

    # print("list of risky investment values")
    # for i, val in enumerate(invest_data.risky_values):
    #     print(f"month: {i + 1}, value: {val}")
    # print("list of medium investment values")
    # for i, val in enumerate(invest_data.medium_values):
    #     print(f"month: {i + 1}, value: {val}")
    # print("list of safe investment values")
    # for i, val in enumerate(invest_data.safe_values):
    #     print(f"month: {i + 1}, value: {val}")
