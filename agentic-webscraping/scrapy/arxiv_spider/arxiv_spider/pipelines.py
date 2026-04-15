import sqlite3
from scrapy.pipelines.files import FilesPipeline

class ArxivSpiderPipeline(FilesPipeline):

    def file_path(self, request, response=None, info=None, *, item=None):
        arxiv_id   = item.get("paper_id", "unknown")
        title      = item.get("title", "unknown")[:80]
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)
        return f"{arxiv_id}_{safe_title}.pdf"

    def item_completed(self, results, item, info):
        for ok, result in results:
            if ok:
                conn = sqlite3.connect("papers.db")
                conn.execute("""
                    UPDATE paper_queue
                    SET pdf_fetched = 1
                    WHERE paper_id = ?
                """, (item["paper_id"],))
                conn.commit()
                conn.close()
                info.spider.logger.info(
                    f"PDF saved + marked done: {item['paper_id']}"
                )
            else:
                info.spider.logger.error(
                    f"PDF download failed: {item['paper_id']} — {result}"
                )
        return item
