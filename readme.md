# Craigslist Crawler

This is a script that monitors the rss feed of craigslist to scrape rental apartment listings for Vancouver. It stores the listing in a database and extracts key characteristics such as area, location and ammenities. This allows for trend analysis, geographical modelling and determining the market value of apartment characteristics (eg. allowing pets).

It also includes scripts to plot the data and publish to a blog.

## To do:

1. Add additional cities (Toronto, Montreal, Portland)
2. Create a predictive model for rents based on observable characteristics
3. Disassoicate the underlying rent trend from changes in observable characteristics
4. Measure the effects of policy changes

## Dependencies
* Feedparser
* ...