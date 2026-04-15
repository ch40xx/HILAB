import scrapy
import sqlite3
from datetime import datetime

class PDFItem(scrapy.Item):
    paper_id  = scrapy.Field()
    title     = scrapy.Field()
    file_urls = scrapy.Field()
    files     = scrapy.Field()

class ArxivSpider(scrapy.Spider):

    name = "pdf_spider"
    allowed_domains = ["arxiv.org","export.arxiv.org"]
    
    custom_settings = {
        "ITEM_PIPELINES" : {
            "arxiv_spider.pipelines.ArxivSpiderPipeline": 1,
        },
        "FILES_STORE": "downloads",
        "DOWNLOAD_DELAY": 3,
        "ROBOTSTXT_OBEY": False,
    }


    def open_spider(self):
        self.conn = sqlite3.connect("papers.db")
        self.cur = self.conn.cursor()

        self.rows = self.cur.execute("""
            SELECT paper_id, title, pdf_url
            FROM paper_queue
            WHERE pdf_fetched = 0
            """).fetchall()

        self.logger.info(f"Found {len(self.rows)} PDFs to download.") 

        self.conn.close()

    async def start(self):
        self.open_spider()
        
        for paper_id, title, pdf_url in self.rows:
            yield scrapy.Request(url = pdf_url,
                                 callback = self.parse_pdf,
                                 meta={
                                    "paper_id": paper_id,
                                    "title" : title
                                 },
                                 errback=self.handle_error,
                                 dont_filter = True,
                                )

    def parse_pdf(self, response):
        item = PDFItem()

        item["paper_id"] = response.meta["paper_id"]
        item["title"] = response.meta["title"]
        item["file_urls"] = [response.url]

        self.logger.info(f"Downloading PDF for: {item["title"][:60]}...")
        yield item 

    def handle_error(self, failure):
        paper_id = failure.request.meta.get('paper_id')
        self.logger.error(f"Failed to download PDF for {paper_id}: {failure.value}")
    
    def close_spider(self, reason):
        if self.conn:
            self.conn.close()
            self.logger.info("Database connection closed.")
