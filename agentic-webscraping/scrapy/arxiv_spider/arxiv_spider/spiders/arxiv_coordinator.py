import scrapy
from datetime import datetime


class ArxivCoordinator(scrapy.Spider):

    name = "arxiv_coordi"
    allowed_domains = ["arxiv.org"]

#    start_urls = ["https://arxiv.org/search/"
#                  "?query={self.query}"
#                  "&searchtype=all&source=header"]
#   You cannot put arguments directly inside start_urls.
#   A start_request(self): must but instantiated.

    async def start(self):
        query = getattr(self, 'query')

        url = (f"https://export.arxiv.org/api/query?search_query=all:{query.replace(' ','+AND+all:')}&start=0&max_results=25&sortBy=submittedDate&sortOrder=descending")

        yield scrapy.Request(url,self.parse)

    def parse(self, response):
        response.selector.remove_namespaces()

        for entry in response.xpath("//entry"):
            abs_url = entry.xpath("id/text()").get()
            paper_id = abs_url.split("/abs/")[-1]
            title = entry.xpath("title/text()").get(default="").strip()
            abstract = entry.xpath("summary/text()").get().strip()
            authors = ", ".join(entry.xpath("author/name/text()").getall())
            html_url = f"https://arxiv.org/html/{paper_id}"
            pdf_url = f"https://arxiv.org/pdf/{paper_id}"

            yield {
                "paper_id" : paper_id,
                "title" : title,
                "abstract" : abstract,
                "authors" : authors,
                "abs_url" : abs_url,
                "html_url" : html_url,
                "pdf_url" : pdf_url,
                "dtime" : datetime.utcnow().isoformat(),
            }




