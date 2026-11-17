from typing import Literal

from pydantic import BaseModel, Field, model_validator


class VariantInput(BaseModel):
    refinancing_interest: float = Field(ge=0.1, le=30, description="Novy urok v %")
    length_change: int = Field(ge=-50, le=50, description="Pridani/odebrani let")
    extra_principal: float = Field(ge=0, le=100_000_000, default=0, description="Navyseni hypoteky v Kc")


class CalculateRequest(BaseModel):
    principal: int = Field(ge=1, le=1_000_000_000, default=3_200_000)
    term: int = Field(ge=2, le=50, default=30)
    rate: float = Field(ge=0.1, le=30, default=2.3)  # percentage
    refinancing_year: int = Field(ge=1, le=49, default=5)
    strategy: Literal["safe", "medium", "risky", "custom"] = "medium"
    custom_rate: float | None = Field(ge=0, le=30, default=None)
    invest_after_payoff: bool = True
    display_mode: Literal["nominal", "real"] = "nominal"
    inflation: float = Field(ge=0, le=30, default=2.0)  # percentage
    variants: list[VariantInput] = Field(
        min_length=1,
        max_length=10,
        default=[
            VariantInput(refinancing_interest=5.2, length_change=0),
            VariantInput(refinancing_interest=5.2, length_change=5),
        ],
    )

    @model_validator(mode="after")
    def check_terms(self):
        if self.refinancing_year >= self.term:
            raise ValueError("Fixace musí skončit dřív, než je hypotéka splacená.")
        for index, variant in enumerate(self.variants, start=1):
            remaining_years = self.term - self.refinancing_year + variant.length_change
            if remaining_years < 1:
                raise ValueError(f"Varianta {index} by po konci fixace neměla žádnou dobu splácení.")
            if remaining_years > 50:
                raise ValueError(f"Varianta {index} by se po konci fixace splácela déle než 50 let.")
        if self.strategy == "custom" and self.custom_rate is None:
            raise ValueError("Zadejte vlastní výnos investic.")
        return self

    @property
    def annual_return(self) -> float:
        if self.strategy == "custom":
            return self.custom_rate / 100
        return STRATEGY_RETURNS[self.strategy]


STRATEGY_RETURNS = {"safe": 0.04, "medium": 0.06, "risky": 0.08}


class PayoffMarker(BaseModel):
    x: int
    y: float
    variant: str
    label: str


class GraphResponse(BaseModel):
    months: list[int]
    series: dict[str, list[float | None]]
    payoff_markers: list[PayoffMarker]


class SummaryResponse(BaseModel):
    summary: list[dict]
    milestones: list[dict]  # {label: str, rows: list[dict], best: str | None}
    recommendation: str | None
    ranked_variants: list[dict]
