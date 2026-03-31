import yfinance as yf
import pandas as pd

TIMEFRAMES = {'1d': 1 / 365, '5d': 1 / 73, '1mo': 1 / 12, '3mo': 1 / 4, '6mo': 1 / 2, '1y': 1, '2y': 2, '5y': 5, '10y': 10, 'ytd': None, 'max': None}
FIXED_INTEREST_RATES = {"safe": 0.04, "medium": 0.06, "risky": 0.08}


class InvestStrategies:
    def __init__(self, time_frame: str = '10y') -> None:
        # timeframe must be one of -> ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
        self.__status = False
        self.time_frame = time_frame

        try:
            self.safe = yf.download("ZN=F", group_by="Ticker", period=time_frame)       # safe strategy     10-Year T-Note Futures,Dec-2024 https://finance.yahoo.com/quote/ZN%3DF/
            self.medium = yf.download("^SPX", group_by="Ticker", period=time_frame)     # medium strategy   S&P 500 index,                  https://finance.yahoo.com/quote/%5ESPX/
            self.risky = yf.download("TSLA", group_by="Ticker", period=time_frame)      # risky strategy    TESLA                           https://finance.yahoo.com/quote/TSLA/
        except:
            print("failed to fetch data")
            return
        else:
            self.__status = True

    def get_status(self) -> bool:
        return self.__status

    # default -> range [-1, 1], call with percent = True to get values in %
    def interest_rates(self, percent=False) -> None | tuple[float, float, float]:
        return (self.calc_interest_rate(self.safe, percent), self.calc_interest_rate(self.medium, percent), self.calc_interest_rate(self.risky, percent)) if self.__status else None

    def calc_interest_rate(self, data: pd.DataFrame, percent: bool) -> float:
        actual_years = TIMEFRAMES[self.time_frame]
        if self.time_frame == "ytd" or self.time_frame == "max":
            actual_years = data.len() / 12
        start_val = float(data.iloc[2][4])
        end_val = float(data.iloc[-1][4])
        return (pow(end_val / start_val, 1 / actual_years) - 1) * (100 if percent else 1)


'''
def main() -> None:
    invs = InvestStrategies()
    if invs.get_status():
        print(invs.interest_rates())


if __name__ == "__main__":
    main()
'''
