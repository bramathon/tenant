import logging
import argparse
import pandas as pd

from dotenv import load_dotenv, find_dotenv
from google.cloud import bigquery

if __name__ == "__main__":
    # SETTINGS
    parser = argparse.ArgumentParser(description="Download the latest data")
    parser.add_argument("--metro", default="vancouver", type=str, help="Which metro area should we grab data for?")
    parser.add_argument("--output_file", default="data/raw/vancouver_data.parquet", type=str, help="Model will be saved in this directory")
    parser.add_argument("--log", default="info", type=str, help="Set the logging level")

    args = parser.parse_args()
    output_file = args.output_file

    # Set log level to specified arg
    loglevel = args.log
    numeric_level = getattr(logging, loglevel.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % loglevel)
    logging.basicConfig(level=numeric_level)

    # Get the credentials
    # find .env automagically by walking up directories until it's found
    dotenv_path = find_dotenv()
    # load up the entries as environment variables
    load_dotenv(dotenv_path)

    # Construct a BigQuery client object.
    client = bigquery.Client()

    query = """
    SELECT *
    FROM `craiglist_crawler.listings`
    WHERE metro = 'vancouver'
    """

    logging.info("Querying data...")
    df = client.query(query).result().to_dataframe()

    logging.info(f"Saving data in {output_file}")
    df.to_parquet(output_file)
