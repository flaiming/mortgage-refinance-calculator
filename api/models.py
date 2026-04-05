from pydantic import BaseModel, Field
from typing import Literal


class VariantInput(BaseModel):
    refinancing_interest: float = Field(ge=0.1, description="Novy urok v %")
    length_change: int = Field(ge=-50, le=50, description="Pridani/odebrani let")
    extra_principal: float = Field(ge=0, default=0, description="Navyseni hypoteky v Kc")


class CalculateRequest(BaseModel):
    principal: int = Field(ge=1, default=2_500_000)
    term: int = Field(ge=2, default=30)
    rate: float = Field(ge=0.1, default=1.69)  # percentage
    refinancing_year: int = Field(ge=1, default=7)
    strategy: Literal["safe", "medium", "risky", "custom"] = "medium"
    custom_rate: float | None = Field(ge=0, default=None)
    invest_after_payoff: bool = False
    display_mode: Literal["nominal", "real"] = "nominal"
    inflation: float = Field(ge=0, default=2.0)  # percentage
    variants: list[VariantInput] = [
        VariantInput(refinancing_interest=4.39, length_change=0),
        VariantInput(refinancing_interest=4.39, length_change=7),
    ]


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
    milestones: list[dict]  # {label: str, rows: list[dict]}
    recommendation: str | None
    ranked_variants: list[dict]
