import os
import scrapy

class HTMLSaverSpider(scrapy.Spider):
    name = "html_saver"
    start_urls = ["https://arxiv.org/html/2604.0735v1"]

    SAVE_DIR = "downloads/html"

    def parse(self, response):
        os.makedirs(self.SAVE_DIR, exist_ok=True)

        page_id = response.url.rstrip("/").split("/")[-1]
        filename = f"{self.SAVE_DIR}/{page_id}.html"

        with open(filename, "wb") as f:
            f.write(response.body)

        self.logger.info(f"Saved HTML → {filename}")

        yield {
            "url":           response.url,
            "local_html":    filename,       # store path in SQLite
            "title":         response.css("title::text").get("").strip(),
        }
