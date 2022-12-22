from pathlib import Path
from typing import List

import pandas as pd

BASE_URL = "https://www.canada.ca/en/revenue-agency/services/charities-giving/other-organizations-that-issue-donation-receipts-qualified-donees/other-qualified-donees-listings"

CRA_LIST_OF_MUNICIPALITIES = {
    "Alberta": f"{BASE_URL}/list-municipalities-alberta.html",
    "British Columbia": f"{BASE_URL}/list-municipalities-british-columbia.html",
    "Manitoba": f"{BASE_URL}/list-municipalities-manitoba.html",
    "New Brunswick": f"{BASE_URL}/list-municipalities-new-brunswick.html",
    "Newfoundland and Labrador": f"{BASE_URL}/list-municipalities-newfoundland-labrador.html",
    "Northwest Territories": f"{BASE_URL}/list-municipalities-northwest-territories.html",
    "Nova Scotia": f"{BASE_URL}/list-municipalities-nova-scotia.html",
    "Nunavut": f"{BASE_URL}/list-municipalities-nunavut.html",
    "Ontario": f"{BASE_URL}/list-municipalities-ontario.html",
    "Prince Edward Island": f"{BASE_URL}/list-municipalities-prince-edward-island.html",
    "Quebec": f"{BASE_URL}/list-municipalities-quebec.html",
    "Saskatchewan": f"{BASE_URL}/list-municipalities-saskatchewan.html",
    "Yukon": f"{BASE_URL}/list-municipalities-yukon.html",
}


def scrape_province_municipalities(province_name: str, url: str) -> pd.DataFrame:
    """
    Scrape the province's municipalities.
    """
    df = pd.read_html(url)[0]
    df["Province"] = province_name
    return df


def scrape_municipalities() -> pd.DataFrame:
    """
    Scape all the provincial municipalities.
    """
    dataframes: List[pd.DataFrame] = []

    for province_name, url in CRA_LIST_OF_MUNICIPALITIES.items():
        dataframes.append(
            scrape_province_municipalities(province_name=province_name, url=url)
        )

    df = pd.concat(dataframes).reset_index()
    df = df[["Name", "Province", "Type", "Status", "Effective date", "Notes"]]

    df["Effective date"] = pd.to_datetime(df["Effective date"])

    df.rename(
        columns={
            "Name": "name",
            "Province": "province",
            "Type": "type",
            "Status": "status",
            "Effective date": "effective_date",
            "Notes": "notes",
        },
        inplace=True,
    )

    df.sort_values(["province", "name"], ascending=True, inplace=True)

    return df


def write_df_to_csv_file(df: pd.DataFrame, path: Path):
    """
    Write the pandas DataFrame to a CSV file.
    """
    df.to_csv(path, index=False)


def main():
    dataset_dir_path = Path(__file__).parent.absolute()
    dataset_csv_path = dataset_dir_path / "canadian-municipalities.csv"

    df = scrape_municipalities()
    write_df_to_csv_file(df, dataset_csv_path)


if __name__ == "__main__":
    main()
