# -*- coding: utf-8 -*-

# Scrapy settings for fang project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# from fake_useragent import UserAgent

BOT_NAME = 'fang'

SPIDER_MODULES = ['fang.spiders']
NEWSPIDER_MODULE = 'fang.spiders'

ROBOTSTXT_OBEY = False

DOWNLOAD_DELAY = 1


# ua = UserAgent().random

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36'
}


#DOWNLOADER_MIDDLEWARES = {
#    'fang.middlewares.FangDownloaderMiddleware': 543,
#}

#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}
TELNETCONSOLE_ENABLED=False
#ITEM_PIPELINES = {
    #'fang.pipelines.FangPipeline': 300,
    #'fang.pipelines.MongoPipeline': 400,
#}

# MONGO_URI = 'localhost'
# MONGO_DB = 'fangtianxia'

# Scrapy-Redis相关配置
# 确保request存储到redis中
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# 确保所有爬虫共享相同的去重指纹
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# 设置redis为item pipeline
ITEM_PIPELINES = {
    'scrapy_redis.pipelines.RedisPipeline': 300
}

# 在redis中保持scrapy-redis用到的队列，不会清理redis中的队列，从而可以实现暂停和恢复的功能。
SCHEDULER_PERSIST = True

# 设置连接redis信息
REDIS_HOST = '192.168.150.128'
REDIS_PORT = 6379