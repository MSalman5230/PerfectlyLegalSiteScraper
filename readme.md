# WebScraper with Scrapy.
It is hobby project, I wanted to download link and size of all the attachment for all the post a users posted in this specific site.
This scraper is built with scrapy framework and stores post details and link of the post and direct download link for the attachment in a MongoDB Collection.

Note:I decided to exclude name of the website because of TOS

# Settings

In **settings.py** you change the setting for MongoDB credential
```python
MONGODB_URI = 'mongodb://user:pass@192.168.1.3:27017'  # Replace with your MongoDB URI
MONGODB_DATABASE = 'DB_Name'  # Replace with your database name
MONGODB_COLLECTION = 'PerfectlyLegalSiteScraper'  # Replace with your collection name
```
If you want can to disable mongodb Connection and enable json export with
Change this to *0* in 

**setting.py**
```python
ITEM_PIPELINES = {
    'PerfectlyLegalSiteScraper.pipelines.MongoDBPipeline': 0,
}

#Then uncommenting this in same file

FEED_FORMAT = 'json'  # Output format (JSON)
FEED_URI = 'output.json'  # Output file path (replace with your desired path)
``````

# Run
```bash
scrapy crawl LegalStuff
```
Name of the crawler can be change in spiders/mainSpider.py
```python
name = "LegalStuff"
```
