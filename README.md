# robotsparser
Python library that parses robots.txt files

## Functionalities

- Automatically discover all sitemap files
- Unzip gziped files
- Fetch all URLs from sitemaps

## Install
```
pip install robotsparser
```

## Usage

```python
from robotsparser.parser import Robotparser

robots_url = "https://www.example.com/robots.txt"
rb = Robotparser(url=robots_url, verbose=True)
# To initiate the crawl of sitemaps and indexed urls. sitemap_crawl_limit argument is optional
rb.read(fetch_sitemap_urls=True, sitemap_url_crawl_limit=5)

# Show information
rb.get_sitemap_indexes() # returns sitemap indexes
rb.get_sitemaps() # returns sitemaps
rb.get_urls() # returns a list of all urls
```

## Crawl in the background using thread

Crawl in the background

This is useful for sites where sitemaps are heavily nested and take a long
time to crawl

While crawling you will be able to access the Robotparser class attributes to fetch
sitemaps or entries

```python
from robotsparser.parser import Robotparser
import threading

if __name__ == '__main__':
    robots_url = "https://www.example.com/robots.txt"
    rb = Robotparser(url=robots_url, verbose=False)

    sitemap_crawl_proc = threading.Thread(target = rb.read, kwargs = {'fetch_sitemap_urls': False}, daemon=True)
    sitemap_crawl_proc.start()

    while sitemap_crawl_proc.is_alive():
        time.sleep(1)
        print(f"entries_count: {len(rb.get_sitemap_entries())}, indexes: {len(rb.get_sitemap_indexes())}")
        # any logic here to get object data
```