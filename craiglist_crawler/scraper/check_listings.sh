#!/bin/bash
cd /home/bram/craiglist_crawler/
python3 scraper/check_listings.py "vancouver"
python3 scraper/check_listings.py "portland"
python3 scraper/check_listings.py "toronto"
python3 scraper/check_listings.py "montreal"
