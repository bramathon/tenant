# Craigslist Crawler

This is a script that monitors the rss feed of craigslist to scrape rental apartment listings for Vancouver. It stores the listings in a database and extracts key characteristics such as area, location and ammenities. This allows for trend analysis, geographical modelling and determining the market value of apartment characteristics.

## Getting the data

To build the latest dataset, download the data from google bigquery.

This is done using the script craiglist_crawler/data/make_dataset.py or, using the target provided in the Makefile.

Ensure your credentials are located in a .env file
