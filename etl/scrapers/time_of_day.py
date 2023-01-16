import datetime
from typing import TypedDict
from pathlib import Path
import pandas as pd
import pytz
from astral import Depression, LocationInfo
from astral.sun import sun
from dateutil import rrule as dateutil_rrule

from etl.settings import DATA_PATH

TORONTO = LocationInfo(
    name="Toronto",
    region="Canada",
    timezone="America/Toronto",
    longitude=-79.373333,
    latitude=43.741667,
)

MARKDALE = LocationInfo(
    name="Markdale",
    region="Canada",
    timezone="America/Toronto",
    longitude=-80.65,
    latitude=44.316667,
)

CITIES = [TORONTO, MARKDALE]


class SunPositions(TypedDict):
    dawn: datetime.datetime
    sunrise: datetime.datetime
    noon: datetime.datetime
    sunset: datetime.datetime
    dusk: datetime.datetime


def get_sun_positions(
    city: LocationInfo,
    date: datetime.date = None,
    dawn_dusk_depression: Depression = Depression.CIVIL,
    tzinfo: datetime.tzinfo = pytz.utc,
) -> pd.DataFrame:
    """
    Returns the sun's positions at different times of the day for a given city
    in a pandas' data frame.
    """
    if date is None:
        tz = pytz.timezone(city.timezone)
        date = tz.normalize(datetime.datetime.now()).date()

    positions: SunPositions = sun(
        observer=city.observer,
        date=date,
        dawn_dusk_depression=dawn_dusk_depression,
        tzinfo=tzinfo,
    )

    df = pd.DataFrame(data=[positions])
    df["name"] = city.name
    df["region"] = city.region
    df["date"] = date
    df["timezone"] = city.timezone
    df["latitude"] = city.latitude
    df["longitude"] = city.longitude

    return df


def write_df_to_csv_file(df: pd.DataFrame, path: Path):
    """
    Write the pandas DataFrame to a CSV file.
    """
    df.to_csv(path, index=False)


def main():
    dataset_dir_path = DATA_PATH / "time-of-day"
    dataset_csv_path = dataset_dir_path / "sun.csv"

    dfs = []

    dates = dateutil_rrule.rrule(
        freq=dateutil_rrule.DAILY,
        dtstart=datetime.date(1986, 9, 19),
        until=datetime.date(2086, 12, 31),
    )

    for city in CITIES:
        for date in dates:
            try:
                dfs.append(get_sun_positions(city, date))
            except Exception:
                pass

    df = pd.concat(dfs)

    write_df_to_csv_file(df, dataset_csv_path)


if __name__ == "__main__":
    main()

