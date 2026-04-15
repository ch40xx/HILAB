import scrapy
import sqlite3


class PDFItem(scrapy.Item):
    paper_id = scrapy.Field()
    title = scrapy.Field()
    file_urls = scrapy.Field()


class ArxivPDFSpider(scrapy.Spider):
    name = "pdf_spider"

    allowed_domains = ["arxiv.org", "export.arxiv.org"]

    custom_settings = {
        "ITEM_PIPELINES": {
            "arxiv_spider.pipelines.ArxivSpiderPipeline": 300,
        },
        "FILES_STORE": "downloads/arxiv_pdfs",
        "DOWNLOAD_DELAY": 5,
        "CONCURRENT_REQUESTS": 2,
        "ROBOTSTXT_OBEY": False,
    }

    def open_spider(self):
        self.conn = sqlite3.connect("papers.db")
        
    def start_requests(self):

        self.open_spider()
        rows = self.conn.execute("""
            SELECT paper_id, title, pdf_url
            FROM paper_queue
            WHERE pdf_fetched = 0
            LIMIT 10
            """).fetchall()

        self.logger.info(f"Found {len(rows)} PDFs to download.")

        for paper_id, title, pdf_url in rows:
            yield scrapy.Request(
                url=pdf_url,
                callback=self.parse_pdf,
                meta={"paper_id": paper_id, "title": title},
                errback=self.handle_error,
                dont_filter=True,
            )

    def parse_pdf(self, response):
        item = PDFItem()
        item["paper_id"] = response.meta["paper_id"]
        item["title"] = response.meta["title"]
        item["file_urls"] = [response.url]

        self.logger.info(f"Yielding PDF: {item['title'][:70]}...")
        yield item

    def handle_error(self, failure):
        paper_id = failure.request.meta.get("paper_id", "unknown")
        self.logger.error(f"Failed to download PDF {paper_id}: {failure.value}")

    def close_spider(self, reason):
        if hasattr(self, 'conn'):
            self.conn.close()
            self.logger.info("Database connection closed.")
