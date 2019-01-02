# -*- coding: utf-8 -*-
import scrapy
import datetime
from myfirstproject.items import MagazineCover

#https://blog.csdn.net/QZC295919009/article/details/42680457
#https://www.pyimagesearch.com/2015/10/12/scraping-images-with-python-and-scrapy/
#https://segmentfault.com/a/1190000009597329
#parse the photos
class MagazineSpider(scrapy.Spider):
    name = 'magazine'
    start_urls = ['https://www.timecoverstore.com/top-category']

    def parse(self,response):
        for href in response.css('div.master-wrapper-content a::attr(href)').extract()[:18]:
            yield response.follow(href,callback = self.parse_cover)
        nexturl = response.css('li.next-page a::attr(href)').extract_first()
        yield response.follow(nexturl,callback=self.parse)

    def parse_cover(self,response):
        img_url = response.css('a.full-size-img::attr(href)').extract_first()

        title = response.css('div.product-group h2::text').extract_first().strip()

        pub =  response.css('div.short-description-date::text').extract_first()



        #传入的参数要求是一个list
        item = MagazineCover(image_urls = [img_url])

        yield item




#parse the text
class QuoteSpider(scrapy.Spider):
    name = 'quotes'
    #allowed_domains = ['example.com']
    start_urls = [
        'http://quotes.toscrape.com/page/1/',
        'http://quotes.toscrape.com/page/2/',
    ]

    """
    name: 用于区别Spider。 该名字必须是唯一的，您不可以为不同的Spider设定相同的名字。
    start_urls: 包含了Spider在启动时进行爬取的url列表。 
    因此，第一个被获取到的页面将是其中之一。 
    后续的URL则从初始的URL获取到的数据中提取。
    parse() 是spider的一个方法。 被调用时，每个初始URL完成下载后生成的 Response 对象将会作为唯一的参数传递给该函数。 
    该方法负责解析返回的数据(response data)，
    提取数据(生成item)以及生成需要进一步处理的URL的 Request 对象。
    """

    def parse(self, response):

        """
        The parse() method usually parses the response,
        extracting the scraped data as dicts and also finding new URLs to
        follow and creating new requests (Request)
        from them.

        """

        for quote in response.css('div.quote'):
            """
            <div class="quote" itemscope itemtype="http://schema.org/CreativeWork">
        
            <span class="text" itemprop="text"> 
        
            <span>by <small class="author" itemprop="author">Marilyn Monroe</small>
            
            """
            yield{
                'text':quote.css('span.text::text').extract_first(),
                'author':quote.css('small.author::text').extract_first(),
                'tag':quote.css('div.tags a.tag::text').extract(),
            }

            #what if we want to scrape the next page?

            """
            <ul class="pager">
                <li class="next">
                    <a href="/page/2/">Next <span aria-hidden="true">&rarr;</span></a>
                </li>
            </ul>
            
            we want the href="XXXX"  XXX 
            
            """
            """
            next_page = response.css('li.next a::attr(href)').extract_first()
            if next_page is not None:
                yield response.follow(next_page,callback = self.parse)

            """

            #shortcut

            for href in response.css('li.next a::attr(href)'):
                yield response.follow(href,callback = self.parse)



#parse the author
class AuthorSpider(scrapy.Spider):
    name = 'author'
    start_urls = ['http://quotes.toscrape.com/']

    def parse(self,response):
        for href in response.css('.author+a::attr(href)'):
            yield response.follow(href,callback = self.parse_author)
        for href in response.css('li.next a::attr(href)'):
            yield response.follow(href,callback = self.parse)
    def parse_author(self,response):

        def extract_with_css(query):
            return response.css(query).extract_first().strip()
        """
        The parse_author callback defines a helper function to extract 
        and cleanup the data from a CSS query and yields the Python dict with the author data.
        :param response: 
        :return: 
        """

        yield{
            'name':extract_with_css('h3.author-title::text'),
            'birthday':extract_with_css('span.author-born-date::text'),
            'birth-loc':extract_with_css('span.author-born-location::text'),
            'bio':extract_with_css('div.author-description::text'),

        }




#parse NME news
class nmeScraper(scrapy.Spider):

    name = 'nme'
    start_urls = ['https://www.nme.com/news/music']

    def parse(self,response):

        #进入该标题对应网址，爬取更详细信息
        for href in response.css('a.entry::attr(href)').extract():
                yield response.follow(href,callback = self.parseNews)

        #爬取下一页
        #for href in response.css('li a.nextpostslink::attr(href)').extract():
         #       yield response.follow(href,callback = self.parse)

    def parseNews(self,response):

        def extract_with_css(query):
            return response.css(query).extract_first().strip()

        yield{
            'headline':extract_with_css('h1.title-primary::text'),
            'author':extract_with_css('div.post-author-info span.author::text'),
            'tag':response.css('div.articleBody a::text').extract()
        }
