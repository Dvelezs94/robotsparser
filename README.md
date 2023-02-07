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

## Multiprocessing usage (crawl in the background)

Crawl in the background and output new entries to file

This is useful for sites where sitemaps are heavily nested and take a long
time to crawl

```python
from robotsparser.parser import Robotparser
import multiprocessing as mp
from sh import tail

if __name__ == '__main__':
    mp.freeze_support()
    robots_url = "https://www.example.com/robots.txt"
    entries_log_file="./entries.log"
    rb = Robotparser(url=robots_url, verbose=False, sitemap_entries_file=entries_log_file)
    sitemap_crawl_proc = mp.Process(target = rb.read, kwargs = {'fetch_sitemap_urls': False})
    sitemap_crawl_proc.start()

    for line in tail("-f", entries_log_file, _iter=True):
        # your logic goes here. each entry is line 1 sitemap
        print(line.replace("\n", "")) # remove line break and print
        # stop once crawl has finished
        if not sitemap_crawl_proc.is_alive():
            break
```