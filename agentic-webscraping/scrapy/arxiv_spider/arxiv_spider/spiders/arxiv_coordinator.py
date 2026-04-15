import scrapy
import sqlite3
from datetime import datetime


class ArxivCoordinator(scrapy.Spider):

    name = "arxiv_coordi"
    allowed_domains = ["arxiv.org","export.arxiv.org"]

    #    start_urls = ["https://arxiv.org/search/"
    #                  "?query={self.query}"
    #                  "&searchtype=all&source=header"]
    #   You cannot put arguments directly inside start_urls.
    #   A start_request(self): must but instantiated.


    MAXCOUNT = 50

    def open_spider(self):
        self.conn = sqlite3.connect("papers.db")
        self.cur = self.conn.cursor()
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS paper_queue (
                paper_id     TEXT PRIMARY KEY,
                title        TEXT,
                abstract     TEXT,
                authors      TEXT,
                abs_url      TEXT,
                pdf_url      TEXT,
                html_url     TEXT,
                dtime        TEXT,
                abs_fetched  INTEGER DEFAULT 0,
                pdf_fetched  INTEGER DEFAULT 0,
                html_fetched INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    async def start(self):
        self.open_spider()

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

            rows = {
                "paper_id" : paper_id,
                "title" : title,
                "abstract" : abstract,
                "authors" : authors,
                "abs_url" : abs_url,
                "html_url" : html_url,
                "pdf_url" : pdf_url,
                "dtime" : datetime.utcnow().isoformat(),
            }

            self.cur.execute("""
                INSERT OR IGNORE INTO paper_queue
                (paper_id, title, abstract, authors, abs_url, html_url, pdf_url, dtime) 
                VALUES
                (:paper_id, :title, :abstract, :authors, :abs_url, :html_url, :pdf_url, :dtime)""",rows)

            self.logger.info(f"Queued: {rows['title'][:60]}..")

        self.conn.commit()


        current_page = int(response.url.split("start=")[1].split("&")[0])
        next_page = current_page + 25
        if next_page <= self.MAXCOUNT:
            url = response.url.replace(f"start={current_page}",f"start={next_page}")
            yield scrapy.Request(url, callback=self.parse)
        else:
            self.close_spider()

    def close_spider(self):
        total = self.cur.execute(
            "SELECT COUNT(*) FROM paper_queue"
        ).fetchone()[0]
        self.logger.info(f"Queue total: {total} papers")
        self.conn.close()
