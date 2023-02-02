from gc import callbacks
import scrapy
import requests
import os
from bs4 import BeautifulSoup


class Books(scrapy.Spider):
    name = "Bags"

    def start_requests(self):
        baseurl = 'https://www.amazon.in/s?k=bags&page='
        baseendurl = '&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_'
        urls = []
        for i in range(20, 21):
            urls.append(baseurl+str(i)+baseendurl+str(i))
            # self.log(urls[i-1])
        for i in range(len(urls)):
            resp = scrapy.Request(url=urls[i], callback=self.parse1)
            yield resp

    def parse1(self, response):
        page = response.css(
            'span[data-component-type="s-search-results"]')
        page = page.css(
            'div.s-result-item[data-component-type]')
        # self.log(page[0])
        # page = [page[i].get() for i in range(0, len(page))]
        item_urls = []
        for i in page:
            page_url = i.css("a.a-link-normal.a-text-normal::attr(href)").get()
            if page_url is not None:
                item_urls.append('https://www.amazon.in' +
                                 page_url)
        self.log(len(page))
        self.log(item_urls)
        for url in item_urls:
            resp = scrapy.Request(url=url, callback=self.parse2)
            resp.meta['url'] = url
            yield resp
        # page=[page[i] for i in range(0,len(page),int(len(page)/4))]
        # for i in page:
        #     resp=scrapy.Request(i,callback=self.parse2)
        #     resp.meta['name']=response.meta['name']+'/'+str(i).split('/')[3].split('-')[0]
        #     self.log(response.meta['name']+'/'+str(i).split('/')[3].split('-')[0])
        #     yield resp
        #     self.log('HI --- 1')

    def parse2(self, responce):
        product_url = responce.meta['url']
        product_name = responce.css(
            'span.a-size-large.product-title-word-break::text').get()
        price = responce.css(
            'span.a-price-whole::text').get()
        rating = responce.css('span.reviewCountTextLinkedHistogram::attr(title)')[
            0].get().split()[0]
        no_of_reviews = responce.css(
            'span[id="acrCustomerReviewText"]::text').get()
        asin = product_url.split('/')[-1]
        descriptions = responce.css(
            'div[id="feature-bullets"]').get()
        description = BeautifulSoup(descriptions).get_text().strip()
        all_tr = responce.css('tr').get()
        self.log(all_tr)
        all_tr = [BeautifulSoup(i, 'html.parser')
                  for i in all_tr if i is not None]

        manufacturer = ''
        for i in all_tr:
            th = i.find('th')
            if th is not None:
                th = th.text
            if th is not None and 'Manufacturer' in th:
                manufacturer = i.find('tr')
                if manufacturer is not None:
                    manufacturer = manufacturer.text
                break
        yield {
            'product_url': product_url,
            'product_name': product_name,
            'price': price,
            'rating': rating,
            'no_of_reviews': no_of_reviews,
            'asin': asin,
            'description': description,
        }
