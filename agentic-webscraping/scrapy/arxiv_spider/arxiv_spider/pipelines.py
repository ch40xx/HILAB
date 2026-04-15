# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.files import FilesPipeline

class ArxivSpiderPipeline(FilesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        arxiv_id = item.get('arxiv_id', 'unknown')
        title = item.get('title', 'unknown')[:100]
        safe_title = "".join(c if c.isalnum() or c in " -_" else "_" for c in title)
        return f"{arxiv_id}_{safe_title}.pdf"
