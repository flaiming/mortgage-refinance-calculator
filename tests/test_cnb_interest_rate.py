import unittest
from unittest.mock import patch, Mock
from cnb_interest_rates import Rates


class TestRates(unittest.TestCase):
    @patch('requests.get')
    def test_rates_success(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 200
        with open('cnb_input1.csv', 'r') as file:
            mock_response.content = file.read().encode('utf-8')
        mock_get.return_value = mock_response

        rates = Rates("test-key")

        self.assertTrue(rates.get_status())
        self.assertEqual(rates.get_date().strftime("%Y-%m-%d"), "2024-10-31")
        self.assertEqual(rates.get_discount_rate(), 3.25)
        self.assertEqual(rates.get_lombard_rate(), 5.25)
        self.assertEqual(rates.get_repo_rate(), 4.25)
        self.assertEqual(rates.get_pribor_rate(), 4.27)

    @patch('requests.get')
    def test_rates_success_none_end(self, mock_get):
        # Mock the API response
        mock_response = Mock()
        mock_response.status_code = 200
        with open('cnb_input2.csv', 'r') as file:
            mock_response.content = file.read().encode('utf-8')
        mock_get.return_value = mock_response

        rates = Rates("test-key")

        self.assertTrue(rates.get_status())
        self.assertEqual(rates.get_date().strftime("%Y-%m-%d"), "2021-02-04")
        self.assertEqual(rates.get_discount_rate(), 0.5)
        self.assertEqual(rates.get_lombard_rate(), 4.1)
        self.assertEqual(rates.get_repo_rate(), 2.4)
        self.assertIsNone(rates.get_pribor_rate())

    @patch('requests.get')
    def test_rates_success_none_middle(self, mock_get):
        # Mock the API response
        mock_response = Mock()
        mock_response.status_code = 200
        with open('cnb_input3.csv', 'r') as file:
            mock_response.content = file.read().encode('utf-8')
        mock_get.return_value = mock_response

        rates = Rates("test-key")

        self.assertTrue(rates.get_status())
        self.assertEqual(rates.get_date().strftime("%Y-%m-%d"), "2024-10-31")
        self.assertEqual(rates.get_discount_rate(), 3.25)
        self.assertIsNone(rates.get_lombard_rate())
        self.assertEqual(rates.get_repo_rate(), 4.25)
        self.assertEqual(rates.get_pribor_rate(), 4.27)

    @patch('requests.get')
    def test_rates_failure_http_code(self, mock_get):
        # Mock the API response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        rates = Rates("test-key")

        self.assertFalse(rates.get_status())
        self.assertIsNone(rates.get_date())
        self.assertIsNone(rates.get_discount_rate())
        self.assertIsNone(rates.get_lombard_rate())
        self.assertIsNone(rates.get_repo_rate())
        self.assertIsNone(rates.get_pribor_rate())


if __name__ == '__main__':
    unittest.main()
