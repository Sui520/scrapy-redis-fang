# -*- coding: utf-8 -*-
import scrapy,re
from fang.items import NewHouseItem,ESFHouseItem
from scrapy_redis.spiders import RedisSpider


class FangSpiderSpider(RedisSpider):
    name = 'fang_spider'
    allowed_domains = ['fang.com']
    #start_urls = ['http://www.fang.com/SoufunFamily.htm']
    redis_key = "fang:start_urls"

    def parse(self, response):
        trs = response.xpath('//div[@class="outCont"]//tr')
        province = None  # 首先设为没有值，下方判断有值在赋给province
        for tr in trs:
            tds = tr.xpath('.//td[not(@class)]')
            province_td = tds[0]  # 提取省份，由于省份不是每一行都有的，所以要过滤一下
            province_text = province_td.xpath('.//text()').get()  # 没有省份的那一行会有空格
            province_text = re.sub(r'\s', '', province_text)  # 用sub替换一下，好判断
            if province_text:
                province = province_text  # 如果有值，就赋给province
            if '其它' in province:  # 不提取海外的
                continue
            city_id = tds[1]  # 接下来提取城市链接和城市名称
            city_links = city_id.xpath('.//a')
            for city_link in city_links:
                city_url = city_link.xpath('.//@href').get()
                city = city_link.xpath('.//text()').get()

                # 构建新房和二手房的url
                url_module = city_url.split('fang')
                prefix = url_module[0]
                domain = url_module[1]
                # 北京特殊，特殊处理一下
                if 'bj' in prefix:
                    newhouse_url = 'http://' + 'newhouse.fang' + domain + 'house/s/'
                    esf_url = 'http://' + 'esf.fang' + domain
                else:
                    # 构建新房的url
                    newhouse_url = prefix + 'newhouse.fang' + domain + 'house/s/'
                    # 构建二手房的url
                    esf_url = prefix + 'esf.fang' + domain
                # meta里面可以携带一些参数信息放到Request里面，在callback函数里面通过response获取
                yield scrapy.Request(url=newhouse_url, callback=self.parse_newhouse, meta={'info': (province, city)})

                yield scrapy.Request(url=esf_url, callback=self.parse_esf, meta={'info': (province, city)})

    def parse_newhouse(self, response):
        # 解析新房具体字段
        # meta里面可以携带一些参数信息放到Request里面，在callback函数里面通过response获取
        province, city = response.meta.get('info')
        lis = response.xpath('//div[contains(@class,"nl_con")]/ul/li')
        for li in lis:
            name = li.xpath(".//div[contains(@class,'house_value')]//div[@class='nlcd_name']/a/text()").get()
            if name:
                name = re.sub(r"\s", "", name)
            house_type_list = li.xpath('.//div[contains(@class,"house_type")]/a/text()').getall()
            # house_type_list = list(map(lambda x:x.replace(' ',''),house_type_list))
            house_type_list = list(map(lambda x: re.sub(r'/s', '', x), house_type_list))
            rooms = list(filter(lambda x: x.endswith('居'), house_type_list))
            area = ''.join(li.xpath('.//div[contains(@class,"house_type")]/text()').getall())
            area = re.sub(r'\s|－|/', '', area)
            address = li.xpath('.//div[@class="address"]/a/@title').get()
            # district_text = ''.join(li.xpath('.//div[@class="address"]/a//text()').getall())
            # district = re.search(r'.*\[(.+)\].*',district_text).group(1)
            sale = li.xpath(".//div[contains(@class,'fangyuan')]/span/text()").get()
            price = "".join(li.xpath(".//div[@class='nhouse_price']//text()").getall())
            price = re.sub(r"\s|广告", "", price)
            # 详情页url
            origin_url = li.xpath(".//div[@class='nlcd_name']/a/@href").get()

            item = NewHouseItem(name=name, rooms=rooms.get(), area=area, address=address,
                                sale=sale, price=price, origin_url=origin_url, province=province, city=city)
            yield item

            # 下一页
            # next_url = response.xpath("//div[@class='page']//a[@class='next']/@href").get()
            # if next_url:
            #     yield scrapy.Request(url=response.urljoin(next_url),
            #                          callback=self.parse_newhouse,
            #                          meta={'info': (provice, city)}
            #                          )

    def parse_esf(self, response):
        # 二手房
        province, city = response.meta.get('info')
        dls = response.xpath("//div[@class='shop_list shop_list_4']/dl")
        for dl in dls:
            item = ESFHouseItem(province=province, city=city)
            name = dl.xpath(".//span[@class='tit_shop']/text()").get()
            if name:
                infos = dl.xpath(".//p[@class='tel_shop']/text()").getall()
                infos = list(map(lambda x: re.sub(r"\s", "", x), infos))
                for info in infos:
                    if "厅" in info:
                        item["rooms"] = info
                    elif '层' in info:
                        item["floor"] = info
                    elif '向' in info:
                        item['toward'] = info
                    elif '㎡' in info:
                        item['area'] = info
                    elif '年建' in info:
                        item['year'] = re.sub("年建", "", info)
                item['address'] = dl.xpath(".//p[@class='add_shop']/span/text()").get()
                # 总价
                item['price'] = "".join(dl.xpath(".//span[@class='red']//text()").getall())
                # 单价
                item['unit'] = dl.xpath(".//dd[@class='price_right']/span[2]/text()").get()
                item['name'] = name
                detail = dl.xpath(".//h4[@class='clearfix']/a/@href").get()
                item['origin_url'] = response.urljoin(detail)
                yield item
        # 下一页
        # next_url = response.xpath("//div[@class='page_al']/p/a/@href").get()
        # if next_url:
        #     yield scrapy.Request(url=response.urljoin(next_url),
        #                          callback=self.parse_esf,
        #                          meta={'info': (provice, city)}
        #                          )












'''
    def parse(self, response):

        # 按省份行分类
        trs = response.xpath('//div[@class="outCont"]//tr')
        province = None  # 省份首先设置为空
        for tr in trs:
            tds = tr.xpath('.//td[not(@class)]')
            # 提取省份，由于省份不是每一行都有的，所以要过滤一下
            province_id = tds[0]
            # 没有省份的那一行会有空格
            province_text = province_id.xpath('.//text()').get()
            # 用sub替换一下，好判断
            province_text = re.sub(r'\s', '', province_text)
            # 如果有值，就赋给province
            if province_text:
                province = province_text
            # 不提取海外的
            if '其他' in province:
                continue
            # 接下来提取城市链接和城市名称
            city_id = tds[1]
            city_links = city_id.xpath('.//a')
            for city_link in city_links:
                city_url = city_link.xpath('.//@href').get()
                city = city_link.xpath('.//text()').get()

                # 构建新房和二手房的url
                url_module = city_url.split('fang')
                prefix = url_module[0]
                domain = url_module[1]
                # 北京特殊，特殊处理一下
                if 'bj' in prefix:
                    # href="http://bj.fang.com/"
                    newhouse_url = 'https://newhouse.fang.com/house/s/'
                    esf_url = 'https://esf.fang.com/'

                else:
                    # https: // sh.newhouse.fang.com / house / s /
                    # https://sh.esf.fang.com/
                    # 构建新房的url
                    newhouse_url = prefix + 'newhouse.' + domain + 'house/s/'
                    # 构建二手房的url
                    esf_url = prefix + 'esf.' + domain
                # meta里面可以携带一些参数信息放到Request里面，在callback函数里面通过response获取
                yield scrapy.Request(url=newhouse_url, callback=self.parse_newhouse, meta={'info': (province, city)})

    def parse_newhouse(self, response):
        # 解析新房具体字段
        # meta里面携带参数信息放到Request里面，在callback函数里面通过response获取
        province, city = response.meta.get('info')
        lis = response.xpath('//div[contains(@class,"nl_con")]/ul/li')
        for li in lis:
            name = li.xpath(".//div[contains(@class,'house_value')]//div[@class='nlcd_name']/a/text()").get()
            if name:
                name = re.sub(r'\s', '', name)
            house_type_list = li.xpath('.//div[contains(@class,"house_type")]/a/text()').getall()
            # house_type_list = list(map(lambda x:x.replace(' ',''),house_type_list))
            house_type_list = list(map(lambda x: re.sub(r'\s', '', x), house_type_list))
            rooms = list(filter(lambda x: x.endswith('居'), house_type_list)).get()
            area = ''.join(li.xpath('.//div[contains(@class,"house_type")]/text()').getall())
            area = re.sub(r'\s|-|/', '', area)
            address = li.xpath('.//div[@class="address"]/a/@title').get()
            sale = li.xpath(".//div[contains(@class,'fangyuan')]/span/text()").get()
            price = "".join(li.xpath(".//div[@class='nhouse_price']//text()").getall())
            price = re.sub(r"\s|广告", "", price)
            # 详情页url
            origin_url = li.xpath(".//div[@class='nlcd_name']/a/@href").get()
            item = NewHouseItem(name=name, rooms=rooms, area=area, address=address,
                                sale=sale, price=price, origin_url=origin_url, province=province, city=city)
            yield item
            # 下一页
            # next_url = response.xpath("//div[@class='page']//a[@class='next']/@href").get()
            # if next_url:
            #     yield scrapy.Request(url=response.urljoin(next_url),
            #                          callback=self.parse_newhouse,
            #                          meta={'info': (provice, city)}
            #                          )

    def parse_esf(self, response):
        # 二手房
        province, city = response.meta.get('info')
        dls = response.xpath("//div[@class='shop_list shop_list_4']/dl")
        for dl in dls:
            item = NewHouseItem,ESFHouseItem(province=province, city=city)
            name = dl.xpath(".//span[@class='tit_shop']/text()").get()
            if name:
                infos = dl.xpath(".//p[@class='tel_shop']/text()").getall()
                infos = list(map(lambda x: re.sub(r"\s", "", x), infos))
                for info in infos:
                    if "厅" in info:
                        item["rooms"] = info
                    elif '层' in info:
                        item["floor"] = info
                    elif '向' in info:
                        item['toward'] = info
                    elif '㎡' in info:
                        item['area'] = info
                    elif '年建' in info:
                        item['year'] = re.sub("年建", "", info)
                item['address'] = dl.xpath(".//p[@class='add_shop']/span/text()").get()
                # 总价
                item['price'] = "".join(dl.xpath(".//span[@class='red']//text()").getall())
                # 单价
                item['unit'] = dl.xpath(".//dd[@class='price_right']/span[2]/text()").get()
                item['name'] = name
                detail = dl.xpath(".//h4[@class='clearfix']/a/@href").get()
                item['origin_url'] = response.urljoin(detail)
                yield item
        # 下一页
        # next_url = response.xpath("//div[@class='page_al']/p/a/@href").get()
        # if next_url:
        #     yield scrapy.Request(url=response.urljoin(next_url),
        #                          callback=self.parse_esf,
        #                          meta={'info': (provice, city)}
        #                          )
'''