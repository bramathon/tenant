#!/bin/bash
# run the rental analysis and upload to blog
cd /home/bram/Documents/craiglist_crawler/

# to update the scripts:
# jupyter nbconvert --to script trend_analysis.ipynb
# jupyter nbconvert --to script monthly_analysis.ipynb

echo "blog_dir = '/home/bram/Documents/blog/content/post/'" > params.py
echo "this_month = '2019-06'" >> params.py
echo "output = True" >> params.py

/home/bram/anaconda3/bin/python /home/bram/Documents/craiglist_crawler/trend_analysis.py 

/home/bram/anaconda3/bin/python /home/bram/Documents/craiglist_crawler/monthly_analysis.py 

# # rsync the blog
# #!/bin/sh
# cd /home/bram/Documents/blog/
# USER=bram_evert_gmail_com
# HOST=heacheswithpictures.com

# DIR=/var/www/headacheswithpictures   # might sometimes be empty!

cd /home/bram/Documents/blog
hugo
gcloud compute scp --project "bram-185008" --zone "us-west1-b" --compress --recurse /home/bram/Documents/blog/public/ my-box:/usr/share/nginx/headacheswithpictures/

exit 0
