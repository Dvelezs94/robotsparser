from robotsparser.parser import Robotparser

robots_url = "https://www.semrush.com/robots.txt"
rb = Robotparser(url=robots_url, verbose=True)
rb.read(fetch_sitemap_urls=True, sitemap_url_crawl_limit=5)
print(rb.get_sitemaps())
print(rb.get_sitemap_entries())

# Show information
urls = rb.get_urls() # returns a list of all urls