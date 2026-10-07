import jieba
import requests
from parsel import Selector
from urllib.parse import urljoin
import re
from queue import Queue


class Crawler:
    def __init__(self, max_num):
        self.visited = list()
        self.content = dict()
        self.max_num = max_num

    def extract_text(self, text):
        """使用正则表达式提取文本中的连续中文内容"""
        pattern = re.compile(r'[\u4e00-\u9fa5]+')
        blocks = pattern.findall(text)
        return ' '.join(blocks)

    def parse(self, response):
        """解析响应内容"""
        sel = Selector(text=response.text)
        # 提取当前页面全部中文内容
        full_text = ' '.join(sel.css('::text').getall())
        content = self.extract_text(full_text)
        # 存储内容
        if content: self.content[response.url] = content
        # 提取<a>标签中的URL
        for link in sel.css('a::attr(href)').getall():
            if not link or link.startswith(('javascript:', '#')): continue
            # 子链接
            url = urljoin(response.url, link)
            # 保存需要访问的子链接
            if url not in self.visited and self.max_num > 0: yield url

    def crawl(self, url, max_depth=2):
        """启动爬虫"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        # 存储url
        self.visited.append(url)
        # 最多递归解析max_num个网页
        while len(self.visited):
            # 弹出需要解析的url
            url = self.visited.pop(0)
            try:
                response = requests.get(url, headers=headers, timeout=20)
                response.encoding = response.apparent_encoding
                # 解析url, 读取文本和内嵌url
                for url in self.parse(response):
                    # 增添 url
                    self.visited.append(url)
                    # 可访问的url数目减1
                    self.max_num = self.max_num - 1

            except Exception as e:
                print(f"爬取失败 {url}: {str(e)}")


# In[3]:


# 第3步测试网络排虫， 最大允许爬1000个网页
crawler = Crawler(max_num=10)
crawler.crawl("https://www.csdn.net")
print(f"总页面数: {len(crawler.content)}")
print(f"总字数: {sum([len(value) for (_, value) in crawler.content.items()])}")

# In[5]:


# 第4步检测爬取结果
print(list(crawler.content.keys()))


# In[ ]:


# 第6步使用jieba分词
for v in crawler.content.values():
    jieba.cut(" ".join(jieba.cut(v)))

