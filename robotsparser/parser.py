import urllib.robotparser
from bs4 import BeautifulSoup
import requests
import gzip
from urllib.parse import urlparse
from typing import Union
from time import sleep

def get_url_file_extension(url) -> str:
    url_parts = urlparse(url)
    return url_parts.path.split(".")[-1]

def parse_urls_from_sitemap(sitemap_url: str, limit: int = 0, delay: int = 0, verbose = False) -> list[str]:
        """
        Reads and saves all urls found in the sitemap entries.

        arguments:
        limit: Max number of sitemaps to crawl for URLs
        """
        urls = []
        extension = get_url_file_extension(sitemap_url)
        r = requests.get(sitemap_url, stream=True)
        if extension == "gzip" or extension == "gz" or extension == "zip":
            if verbose:
                print("Gziped entry found")
            xml = gzip.decompress(r.content)
            bsFeatures = "xml"
        else:
            xml = r.text
            bsFeatures = "lxml"
        soup = BeautifulSoup(xml, features=bsFeatures)
        urlTags = soup.find_all("url")
        for url in urlTags:
            urls.append(url.findNext("loc").text)
        sleep(delay)
        if verbose:
            print(f"Found {len(urls)} urls")
        return urls

class Robotparser:
    def __init__(self, url: str, verbose: bool = False):
        self.robots_url = url
        self.urobot = urllib.robotparser.RobotFileParser()
        self.urobot.set_url(self.robots_url)
        self.urobot.read()
        self.site_maps = self.urobot.site_maps()
        self.verbose = verbose
        self._fetched = False
        self.url_entries = []

    def read(self, fetch_sitemap_urls = True, sitemap_url_crawl_limit=0, delay=0):
        if not self.site_maps:
            raise Exception(f"No sitemaps found on {self.robots_url}")
        self._fetch_sitemaps()
        if fetch_sitemap_urls:
            self._fetch_urls(limit=sitemap_url_crawl_limit, delay=delay)

    def _fetch_sitemaps(self) -> None:
        """
        Reads and saves all sitemap entries.
        """
        # loop through each sitemap 
        sitemap_entries = []
        for site in self.site_maps:
            extension = get_url_file_extension(site)
            r = requests.get(site, stream=True)
            if extension == "gzip" or extension == "gz" or extension == "zip":
                if self.verbose:
                    print("Gziped sitemap found")
                xml = gzip.decompress(r.content)
                bsFeatures = "xml"
            else:
                xml = r.text
                bsFeatures = "lxml"
            soup = BeautifulSoup(xml, features=bsFeatures)
            sitemapTags = soup.find_all("sitemap")
            for sitemap in sitemapTags:
                sitemap_entries.append(sitemap.findNext("loc").text)

        self.sitemap_entries = sitemap_entries
        self._fetched = True
        if self.verbose:
            print(f"Found {len(self.sitemap_entries)} sitemap entries")

    def _fetch_urls(self, limit: int = 0, delay: int = 0) -> None:
        """
        Reads and saves all urls found in the sitemap entries.

        arguments:
        limit: Max number of sitemaps to crawl for URLs
        """
        urls = []
        sitemaps_crawled = 0
        self._validate_fetch()
        print(f"Limit is set to {limit} sitemaps to crawl") if self.verbose and limit else None
        for entry in self.sitemap_entries:
            if limit > 0 and sitemaps_crawled >= limit:
                break
            sitemaps_crawled += 1
            print(f"Processing {entry}") if self.verbose else None
            urls = parse_urls_from_sitemap(entry)
        self.url_entries = urls
        if self.verbose:
            print(f"Found {len(self.url_entries)} urls")
    
    def get_sitemaps(self) -> Union[list[str], None]:
        """
        Returns a list of all the sitemaps found
        """
        self._validate_fetch()
        return self.site_maps

    def get_sitemap_entries(self) -> list[str]:
        self._validate_fetch()
        return self.sitemap_entries

    def get_urls(self):
        return self.url_entries

    def _validate_fetch(self):
        if not self._fetched:
            raise Exception("You need to run fetch_sitemaps() method")