from robotsparser.parser import Robotparser

robots_url = "https://www.vivanuncios.com.mx/robots.txt"
rb = Robotparser(url=robots_url, verbose=True)
rb.read(fetch_sitemap_urls=False, sitemap_url_crawl_limit=5)
print("INDEXES")
print(rb.sitemap_entries)
print("ENTRIES")
print(rb.sitemap_indexes)

# # print(rb.get_sitemaps())
# # print(rb.get_sitemap_entries())

# # # Show information
urls = rb.get_urls() # returns a list of all urls
print("URLS")
print(urls)