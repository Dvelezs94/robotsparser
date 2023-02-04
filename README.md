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