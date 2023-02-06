from bs4 import BeautifulSoup
import requests
import gzip
from urllib.parse import urlparse
from typing import Union
from time import sleep

"""
Main parser script. This fetches and parses sitemap indexes to find all sitemaps 
which are the ones that contain the URLS. see http://bit.ly/3YkUyJx.
"""

def get_url_file_extension(url) -> str:
    url_parts = urlparse(url)
    return url_parts.path.split(".")[-1]

def parse_urls_from_sitemap(sitemap_url: str, limit: int = 0, delay: int = 0, verbose = False) -> set[str]:
        """
        Reads and saves all urls found in the sitemap entries.

        arguments:
        limit: Max number of sitemaps to crawl for URLs
        """
        urls = set()
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
            urls.add(url.findNext("loc").text)
        sleep(delay)
        if verbose:
            print(f"Found {len(urls)} urls")
        return urls

def robotsparser_sitemap_factory(sitemaps_list: set[str], verbose = False):
    """
    returns a Robotparser object with sitemaps_list as robot_sitemaps.
    This is useful for websites that dont have any robots.txt but do have sitemaps

    Usage:
    sitemaps_list = ["https://site1.com/sitemap.xml"]
    rb = robotsparser.robotsparser_sitemap_factory(sitemaps_list)
    rb.read()
    """
    rb = Robotparser(url=None, verbose=verbose)
    rb.robot_sitemaps = sitemaps_list
    return rb

class Robotparser:
    def __init__(self, url: Union[str, None], verbose: bool = False):
        self.robots_url = url
        
        # this gets all top level sitemaps using urobot
        # the problem with this is that it doesnt differenciate between a
        # sitemap and a sitemap index
        self.robot_sitemaps = set()
        self.verbose = verbose
        self._fetched = False
        # we use sets to avoid duplication and keep order
        self.url_entries = set()
        self.sitemap_indexes = set()
        self.sitemap_entries = set()
        if self.robots_url:
            self.get_sitemaps_from_robots()


    def parse_robots_file(self, lines: list[str]):
        """Parse the input lines from a robots.txt file.
        We only extract the lines that start with sitemap
        """
        for line in lines:
            if len(line) > 0:
                line = line.lower()
                line = line.strip()
                line = line.split(':', 1)
                if line[0] == "sitemap":
                    self.robot_sitemaps.add(line[1])

    def get_sitemaps_from_robots(self) -> None:
        print("getting robots")
        r = requests.get(self.robots_url)
        if r.status_code in range(200,299):
            self.parse_robots_file(r.text.splitlines())
        else:
            print(f"Could not access robots.txt file, got {r.status_code}")
        return None
            
    def read(self, fetch_sitemap_urls = True, sitemap_url_crawl_limit=0, delay=0):
        if not self.robot_sitemaps:
            raise Exception(f"No sitemaps found on {self.robots_url}")
        self._fetched = True
        for sitemap in self.robot_sitemaps:
            self._categorize_sitemap(sitemap)
        if self.verbose:
            print(f"Found {len(self.sitemap_entries)} sitemap entries and {len(self.sitemap_indexes)} sitemap indexes")
        # save urls from sitemap entries if true
        if fetch_sitemap_urls:
            self._fetch_urls(limit=sitemap_url_crawl_limit, delay=delay)

    @staticmethod
    def _is_sitemap_index(sitemap_soup: BeautifulSoup):
        """
        Returns true if given sitemap (provided as a BeautifulSoup object) is index
        """
        is_index = False
        if sitemap_soup.find("sitemapindex"):
            is_index = True
        return is_index
    
    @staticmethod
    def _is_sitemap_entry(sitemap_soup: BeautifulSoup) -> bool:
        """
        Returns true if given sitemap (provided as a BeautifulSoup object) contains
        a urlset tag, which means its a valid sitemap
        """
        contains_urlset = False
        if sitemap_soup.find("urlset"):
            contains_urlset = True
        return contains_urlset
    
    @staticmethod
    def _is_html(html_soup: BeautifulSoup) -> bool:
        """
        Returns true if given html (provided as a BeautifulSoup object) contains
        an html tag, which means its a valid html document
        """
        contains_html = False
        if html_soup.find("urlset"):
            contains_html = True
        return contains_html

    @staticmethod
    def _url_is_xml(url: str) -> bool:
        """
        Returns true if url is an xml
        """
        is_xml = False
        if "xml" in urlparse(url).path:
            is_xml = True
        return is_xml

    def _categorize_sitemap(self, sitemap_website: str) -> None:
        """
        THIS IS A RECURSIVE FUNCTION, WHICH MEANS IT CALLS ITSELF EVERY TIME IT CAN,
        SO BE CAREFUL CHANGING IT.

        input: a sitemap website (could be from index or from urlset), it will categorize
        the website if its a valid entry 
        
        Finds all sitemaps from the robot_sitemaps which is probably a sitemap index
        if its not, then it it is moved as a sitemap entry which contains urls

        a url in a sitemap could be an actual site or another url which aims to another site, recursively,
        so we need to dig down deep until we dont find any other sitemap or sitemap index
        """
        # if an xml doc, it means it is either a sitemap or sitemap index
        # print(f"categorizing {sitemap_website}") if self.verbose else None
        if self._url_is_xml(sitemap_website):
            r = requests.get(sitemap_website, stream=True)
            extension = get_url_file_extension(sitemap_website)
            if extension == "gzip" or extension == "gz" or extension == "zip":
                if self.verbose:
                    print("Gziped sitemap found")
                xml = gzip.decompress(r.content)
                bsFeatures = "xml"
            else:
                xml = r.text
                bsFeatures = "lxml"
            soup = BeautifulSoup(xml, features=bsFeatures)
            if self._is_sitemap_index(soup):
                # print(f"new sitemap index {sitemap_website}") if self.verbose else None
                self.sitemap_indexes.add(sitemap_website)
                sitemapTags = soup.find_all("sitemap")
                for sitemap in sitemapTags:
                    new_url = sitemap.findNext("loc").text
                    
                    # if its a sitemap index, then we rerun this function on the new url
                    self._categorize_sitemap(sitemap.findNext("loc").text)
            # sitemap entries could also work as sitemap indexes (some sites do that),
            # We are still missing that part to make sure the loc is an actual website,
            # and not a sitemap index
            elif self._is_sitemap_entry(soup):
                self.sitemap_entries.add(sitemap_website)
        return None

    def _fetch_urls(self, limit: int = 0, delay: int = 0) -> None:
        """
        Reads and saves all urls found in the sitemap entries.

        arguments:
        limit: Max number of sitemaps to crawl for URLs
        """
        self._validate_fetch()
        urls = set()
        sitemaps_crawled = 0
        print(f"Limit is set to {limit} sitemaps to crawl") if self.verbose and limit else None
        for entry in self.sitemap_entries:
            if limit > 0 and sitemaps_crawled >= limit:
                break
            sitemaps_crawled += 1
            urls = set(parse_urls_from_sitemap(entry))
            for url in urls:
                self.url_entries.add(url)
                print(url) if self.verbose else None
        if self.verbose:
            print(f"Found {len(self.url_entries)} urls")
    

    def get_sitemap_indexes(self) -> set[str]:
        self._validate_fetch()
        return self.sitemap_indexes

    def get_sitemap_entries(self) -> set[str]:
        self._validate_fetch()
        return self.sitemap_entries

    def get_urls(self):
        self._validate_fetch()
        return self.url_entries

    def _validate_fetch(self):
        if not self._fetched:
            raise Exception("You need to run read() method")