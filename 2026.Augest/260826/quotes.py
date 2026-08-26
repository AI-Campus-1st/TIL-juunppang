import scrapy

class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    start_urls =['https://quotes.toscrape.com/']

    def parse(self, response):
        for b in response.css('div.quote'):
            yield{
                'text': b.css('span.text::text').get(),
                'author': b.css('small.author::text').get(),
                'tag': ','.join(b.css('div.tags a.tag::text').getall()),
            }
        nxt = response.css('li.next a::attr(href)').get()
        if nxt:
            yield response.follow(nxt, self.parse)