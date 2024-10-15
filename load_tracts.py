import logging
from pathlib import Path
import tomli

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.validation import Validator, ValidationError

from loader import build_workflow, LoadFileType, StopThePresses

from tiger.app_logger import setup_logging
from tiger.connection import db_engine


with open("config.toml", "rb") as f:
    config = tomli.load(f)


logger = logging.getLogger(config["app"]["name"])
setup_logging()


def prepare_2000_tracts(year, tracts):
    logger.info(tracts.columns)
    logger.info("\n" + str(tracts[tracts.columns[:5]].head()))
    logger.info("\n" + str(tracts[tracts.columns[5:]].head()))
    
    return tracts.rename(
        columns={
            "STATEFP00": "state",
            "COUNTYFP00": "county",
            "TRACTCE00": "tract",
            "CTIDFP00": "geoid",
            "NAMELSAD00": "description",
            "MTFCC00": "mtfcc",
            "FUNCSTAT00": "funcstat",
            "ALAND00": "land_area",
            "AWATER00": "water_area",
        }
    ).assign(
        year=int(float(year)),  # Meh!
        long_geoid=lambda df: "14000US" + df["geoid"].astype("str"),
    )[
        [
            "state",
            "county",
            "tract",
            "geoid",
            "long_geoid",
            "description",
            "mtfcc",
            "funcstat",
            "land_area",
            "water_area",
            "year",
            "geometry",
        ]
    ]


def prepare_2010_tracts(year, tracts):
    return tracts.rename(
        columns={
            "STATEFP10": "state",
            "COUNTYFP10": "county",
            "TRACTCE10": "tract",
            "GEOID10": "geoid",
            "NAMELSAD10": "description",
            "MTFCC10": "mtfcc",
            "FUNCSTAT10": "funcstat",
            "ALAND10": "land_area",
            "AWATER10": "water_area",
        }
    ).assign(
        year=int(float(year)),  # Meh!
        long_geoid=lambda df: "14000US" + df["geoid"].astype("str"),
    )[
        [
            "state",
            "county",
            "tract",
            "geoid",
            "long_geoid",
            "description",
            "mtfcc",
            "funcstat",
            "land_area",
            "water_area",
            "year",
            "geometry",
        ]
    ]


def prepare_2020_tracts(year, tracts):
    return tracts.rename(
        columns={
            "STATEFP": "state",
            "COUNTYFP": "county",
            "TRACTCE": "tract",
            "GEOID": "geoid",
            "NAMELSAD": "description",
            "MTFCC": "mtfcc",
            "FUNCSTAT": "funcstat",
            "ALAND": "land_area",
            "AWATER": "water_area",
        }
    ).assign(
        year=int(float(year)),  # Meh!
        long_geoid=lambda df: "14000US" + df["geoid"].astype("str"),
    )[
        [
            "state",
            "county",
            "tract",
            "geoid",
            "long_geoid",
            "description",
            "mtfcc",
            "funcstat",
            "land_area",
            "water_area",
            "year",
            "geometry",
        ]
    ]


def prepare_tracts(tracts):
    def is_valid_year(year: str):
        if not year.isnumeric():
            raise ValidationError(message="Year provided must be an integer")

        if not ((1900 < int(year) < 2100) and (int(year) % 10 == 0)):
            raise ValidationError(
                message="The year provided must correspond to a dicenial year (ends in 0, e.g. 2010)"
            )

        return True

    year_validator = Validator.from_callable(is_valid_year)

    year = prompt(
        "What is the year of this census tract file? ", validator=year_validator
    )

    if year == "2020":
        return prepare_2020_tracts(year, tracts)
    elif year == "2010":
        return prepare_2010_tracts(year, tracts)
    elif year == "2000":
        return prepare_2000_tracts(year, tracts)
    else:
        raise StopThePresses(f"There is no prepared process for {year} tracts.")


if __name__ == "__main__":
    workflow = build_workflow(
        config,
        "tracts",
        Path.cwd(),
        prepare_tracts,
        db_engine,
        LoadFileType.GEOJSON,
    )

    workflow()
