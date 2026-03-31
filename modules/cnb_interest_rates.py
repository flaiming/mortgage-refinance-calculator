import csv
from datetime import datetime
from dotenv import load_dotenv
from io import StringIO
import os
import requests


# https://www.cnb.cz/arad/#/cs/display_link/set_1119__
# SFTP02M11 -> Diskontní sazba
# SFTP03M11 -> Lombardní sazba
# SFTP01M11 -> Repo sazba - 2 týdny
# SFTP04M2102 -> PRIBOR - 7 dní

EMPTY = {"", "NaN"}


class Rates:
    def __init__(self, api_key: str) -> None:
        url = "https://www.cnb.cz/aradb/api/v1/data-trans?set_id=1119&months_before=24&api_key=" + api_key
        self.__status = False
        self.__date: None | datetime = None         # date of the data
        self.__SFTP01M11: None | float = None       # 2T repo sazba - 2 týdny
        self.__SFTP02M11: None | float = None       # Diskontní sazba
        self.__SFTP03M11: None | float = None       # Lombardní sazba
        self.__SFTP04M2102: None | float = None     # PRIBOR - 7 dní

        response = requests.get(url)
        if response.status_code == 200:
            print("API fetch successful")
            self.__status = True
            csv_content = response.content.decode('utf-8')
            csv_reader = csv.reader(StringIO(csv_content), delimiter=";")
            next(csv_reader)    # skip csv header
            latest_rates = next(csv_reader)
            date = latest_rates[0]
            self.__date = datetime(int(date[0:4]), int(date[4:6]), int(date[6:8]))
            self.__SFTP01M11 = float(latest_rates[3].replace(',', '.')) if latest_rates[3] not in EMPTY else None
            self.__SFTP02M11 = float(latest_rates[1].replace(',', '.')) if latest_rates[1] not in EMPTY else None
            self.__SFTP03M11 = float(latest_rates[2].replace(',', '.')) if latest_rates[2] not in EMPTY else None
            self.__SFTP04M2102 = float(latest_rates[4].replace(',', '.')) if len(latest_rates) == 5 else None

        else:
            print("Failed to fetch data from the API")

    def get_discount_rate(self) -> None | float:
        return self.__SFTP02M11

    def get_lombard_rate(self) -> None | float:
        return self.__SFTP03M11

    def get_repo_rate(self) -> None | float:
        return self.__SFTP01M11

    def get_pribor_rate(self) -> None | float:
        return self.__SFTP04M2102

    def get_date(self) -> None | datetime:
        return self.__date

    def get_status(self) -> bool:
        return self.__status


def main() -> None:
    load_dotenv()
    key = os.getenv('ARAD_API_KEY')
    rates = Rates(key)
    print(f"Status: {rates.get_status()}")
    print(f"Date: {rates.get_date()}")

    print(f"Repo sazba: {rates.get_repo_rate()}")
    print(f"Diskontní sazba: {rates.get_discount_rate()}")
    print(f"Lombardní sazba: {rates.get_lombard_rate()}")


if __name__ == "__main__":
    main()
