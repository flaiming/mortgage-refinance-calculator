class Taxes:
    def __init__(
        self,
        interests_paid: list[float],
        yearly_interest_deduction_limit: float = 150000,
        tax_rate: float = 0.15,
    ):
        self.interests_paid = interests_paid
        self.yearly_interest_deduction_limit = yearly_interest_deduction_limit
        self.tax_rate = tax_rate
        self.interests_yearly: list[float] = []
        self.deductible_interests_yearly: list[float] = []
        self.tax_savings_yearly: list[float] = []

    def aggregate_yearly_interests(self) -> list[float]:
        if self.interests_yearly:
            return self.interests_yearly

        months_in_year = 12
        for i in range(0, len(self.interests_paid), months_in_year):
            yearly_sum = sum(self.interests_paid[i : i + months_in_year])
            self.interests_yearly.append(round(yearly_sum, 2))
        return self.interests_yearly

    def calculate_yearly_deductible_interests(self) -> list[float]:
        if self.deductible_interests_yearly:
            return self.deductible_interests_yearly

        for yearly_interest in self.aggregate_yearly_interests():
            self.deductible_interests_yearly.append(min(yearly_interest, self.yearly_interest_deduction_limit))
        return self.deductible_interests_yearly

    def calculate_yearly_tax_savings(self) -> list[float]:
        if self.tax_savings_yearly:
            return self.tax_savings_yearly

        for deductible_interest in self.calculate_yearly_deductible_interests():
            self.tax_savings_yearly.append(round(deductible_interest * self.tax_rate, 2))
        return self.tax_savings_yearly

    def calculate_total_tax_savings(self) -> float:
        return round(sum(self.calculate_yearly_tax_savings()), 2)


if __name__ == "__main__":
    interests = [1000 for _ in range(24)]
    taxes = Taxes(interests)
    print(taxes.calculate_yearly_tax_savings())
