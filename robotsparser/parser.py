import urllib.robotparser
from bs4 import BeautifulSoup
import requests
import gzip
from urllib.parse import urlparse

def get_url_file_extension(url) -> str:
    url_parts = urlparse(url)
    return url_parts.path.split(".")[-1]

class Robotparser:
    def __init__(self, url: str, verbose : bool = False):
        self.robots_url = url
        self.urobot = urllib.robotparser.RobotFileParser()
        self.urobot.set_url(self.robots_url)
        self.urobot.read()
        self.site_maps = self.urobot.site_maps()
        self.verbose = verbose
        self._fetched = False

    def read(self):
        if not self.site_maps:
            raise Exception(f"No sitemaps found on {self.robots_url}")
        self._fetch_sitemaps()
        self._fetch_urls()

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

    def _fetch_urls(self) -> None:
        """
        Reads and saves all urls found in the sitemap entries.
        """
        urls = []
        self._validate_fetch()
        for entry in self.sitemap_entries:
            if self.verbose:
                print(f"Processing {entry}")
            extension = get_url_file_extension(entry)
            r = requests.get(entry, stream=True)
            if extension == "gzip" or extension == "gz" or extension == "zip":
                if self.verbose:
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
        self.url_entries = urls
        if self.verbose:
            print(f"Found {len(self.url_entries)} urls")
    
    def get_sitemaps(self) -> list[str] | None:
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