# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


def clean_text(t):
    return t.strip()


class CleanPipeline:
    def process_item(self, item, spider):
        # item['text'] = clean_text(item['text']).replace("\u201c",'').replace("\u201d",'')
        item['text'] = clean_text(item['text']).strip("\u201c\u201d")
        item['author'] = clean_text(item['author'])
        if not item['text']:
            from scrapy.exceptions import DropItem
            raise DropItem ('내용 없음')
        return item

