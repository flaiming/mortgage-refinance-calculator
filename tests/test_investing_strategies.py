import unittest
from unittest.mock import patch, Mock
import pandas as pd
from investing_strategies import InvestStrategies


def file_to_df(file_path: str) -> pd.DataFrame:
        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
            return pd.DataFrame()

class TestInvestStrategies(unittest.TestCase):
    @patch('yfinance.download')
    def test_invest_strategies_success_all(self, mock_download):
        mock_data_safe = file_to_df('ZN=F.csv')
        mock_data_medium = file_to_df('^SPX.csv')
        mock_data_risky = file_to_df('TSLA.csv')
        mock_download.side_effect = [mock_data_safe, mock_data_medium, mock_data_risky]

        invs = InvestStrategies(time_frame='10y')

        self.assertTrue(invs.get_status())
        a, b, c = invs.interest_rates()
        self.assertEqual(round(a, 2), round(-0.014868835044711814, 2))
        self.assertEqual(round(b, 2), round(0.11156857467454473, 2))
        self.assertEqual(round(c, 2), round(0.35772018365491576, 2))

    @patch('yfinance.download')
    def test_invest_strategies_failure(self, mock_download):
        mock_download.side_effect = Exception("API call failed")

        invs = InvestStrategies(time_frame='10y')

        self.assertFalse(invs.get_status())
        self.assertIsNone(invs.interest_rates())


if __name__ == '__main__':
    unittest.main()