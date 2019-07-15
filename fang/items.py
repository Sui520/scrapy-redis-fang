# -*- coding: utf-8 -*-
import scrapy
from scrapy import Field

class NewHouseItem(scrapy.Item):

    # 省份
    province = Field()
    # 城市
    city = Field()
    # 小区名字
    name = Field()
    # 价格
    price = Field()
    # 几居室，这是一个列表
    rooms = Field()
    # 面积
    area = Field()
    # 地址
    address = Field()

    sale = Field()
    # 房天下详情url
    origin_url = Field()


class ESFHouseItem(scrapy.Item):
    # 省份
    province = Field()
    # 城市
    city = Field()
    # 小区名字
    name = Field()
    # 几室几厅
    rooms = Field()
    # 层
    floor = Field()
    # 朝向
    toward = Field()
    # 年代
    year = Field()
    # 地址
    address = Field()
    # 建筑面积
    area = Field()
    # 总价
    price = Field()
    # 单价
    unit = Field()
    # 详情页url
    origin_url = Field()
