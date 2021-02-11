import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from nomuraholdings.items import Article


class NomuraSpider(scrapy.Spider):
    name = 'nomura'
    start_urls = ['https://www.nomuraholdings.com/news/nr/index.html']

    def parse(self, response):
        links = response.xpath('//table[@class="js-selectList"]//a/@href').getall()
        yield from response.follow_all(links, self.parse_year)

    def parse_year(self, response):
        links = response.xpath('//p[@class="c-List-info__link"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@class="u-h1"]/text()').get()
        if title:
            title = title.strip()
        else:
            return

        date = response.xpath('//div[@class="news-header__date"]/p/text()[1]').get()
        if date:
            date = datetime.strptime(date.strip(), '%B %d, %Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//p[@class="news-paragraph"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
