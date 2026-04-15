import os
import scrapy
import sqlite3
from datetime import datetime

class HTMLSpider(scrapy.Spider):
    name = "html_spider"
    
    def open_spider(self):
        self.conn = sqlite3.connect("papers.db")
        self.cur = self.conn.cursor()
        self.rows = self.cur.execute("""
            SELECT paper_id,html_url
            FROM paper_queue
            WHERE html_fetched =  0
            """).fetchall()

        self.conn.close()
    
    async def start(self):

        self.open_spider()

        for paper_id,html_url in self.rows:
            yield scrapy.Request(url=html_url,
                                 meta={"paper_id":paper_id},
                                 callback = self.parse_html
                                 )


    SAVE_DIR = "downloads/html"

    def parse_html(self, response):
        paper_id = response.meta['paper_id'] 

        os.makedirs(self.SAVE_DIR, exist_ok=True)
        filepath = f"{self.SAVE_DIR}/{paper_id}.html"

        with open(filepath, "wb") as f:
            f.write(response.body)

        conn = sqlite3.connect("papers.db")
        cur = conn.cursor()
        cur.execute("""
            UPDATE paper_queue
            SET html_fetched = 1
            WHERE paper_id = ?
            """,(paper_id,))
        conn.commit()
        conn.close()
        
        self.logger.info(f"Saved HTML → {filepath}")


        yield {
            "url":           response.url,
            "local_html":    filepath,
        }
