import scrapy
from w3lib.html import remove_tags
from arxiv_spider.items import ArxivSpiderItem 


class ArxivSpider(scrapy.Spider):
    name = "arxiv_pdf_downloader"
    allowed_domains = ["arxiv.org"]
    start_urls = ["https://arxiv.org/list/physics.app-ph/new"]

    def parse(self, response):
        for link in response.css("dl dt"):
            url = link.css("a[href*='/abs/']::attr(href)").getall()
 
            yield from response.follow_all(url, self.parse_abs)

    def parse_abs(self, response):
        title = response.css("h1.title::text").get().strip()
        arxiv_id = response.url.split("/abs/")[-1].strip()
        authors = response.css("div.authors a::text").getall()
        r_abs = response.css("blockquote.abstract.mathjax").get()
        c_abs =  ' '.join(remove_tags(r_abs).split())[9:]
        pdf_url = f'https://arxiv.org/pdf/{arxiv_id}.pdf'


        item = ArxivSpiderItem() 
        item['title'] = title
        item['arxiv_id'] = arxiv_id
        item['file_urls'] = [pdf_url]

#        yield {
#                "title" : title, 
#                "arxiv_id" : arxiv_id,
#                "authors" : authors,
#                "abstract" : c_abs,
#                "url" : pdf_url url doesn't work for downloading so "file_urls" is the set standard
#        }

        yield item
