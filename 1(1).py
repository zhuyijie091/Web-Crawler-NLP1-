import jieba
import requests
from parsel import Selector
from urllib.parse import urljoin
import re
from queue import Queue


class Crawler:
    def __init__(self, max_num):
        self.visited = set()  # 使用集合避免重复访问
        self.content = dict()  # 存储页面原始文本
        self.segmented_content = dict()  # 存储分词结果
        self.max_num = max_num  # 最大爬取页面数

    def extract_text(self, text):
        """提取中文内容并用空格连接非连续部分"""
        pattern = re.compile(r'[\u4e00-\u9fa5]+')
        blocks = pattern.findall(text)
        return ' '.join(blocks)

    def parse(self, response):
        """解析页面内容并提取链接"""
        sel = Selector(text=response.text)
        # 提取所有文本并过滤非中文
        full_text = ' '.join(sel.css('::text').getall())
        content = self.extract_text(full_text)
        # 提取所有有效链接
        links = []
        for link in sel.css('a::attr(href)').getall():
            if not link or link.startswith(('javascript:', '#')):
                continue
            url = urljoin(response.url, link)
            links.append(url)
        return content, links

    def crawl(self, start_url, max_depth=2):
        """广度优先爬取，支持深度限制"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        queue = Queue()
        queue.put((start_url, 0))
        self.visited.add(start_url)

        while not queue.empty() and self.max_num > 0:
            url, depth = queue.get()
            if depth > max_depth:
                continue

            try:
                response = requests.get(url, headers=headers, timeout=20)
                response.encoding = response.apparent_encoding
                content, links = self.parse(response)

                # 存储内容并分词
                if content:
                    self.content[url] = content
                    words = list(jieba.cut(content))
                    self.segmented_content[url] = words

                # 每处理一个页面，配额减1
                self.max_num -= 1

                # 添加子链接到队列
                for link in links:
                    child_url = urljoin(url, link)
                    if child_url not in self.visited and depth + 1 <= max_depth:
                        self.visited.add(child_url)
                        queue.put((child_url, depth + 1))

            except Exception as e:
                print(f"爬取失败 {url}: {str(e)}")


# 测试爬虫
crawler = Crawler(max_num=10)
crawler.crawl("https://www.csdn.net", max_depth=1)

# 输出结果
print(f"总页面数: {len(crawler.content)}")
print(f"总字数: {sum(len(text) for text in crawler.content.values())}")

# 示例页面分词结果
sample_url = "https://www.csdn.net/"
if sample_url in crawler.segmented_content:
    print(f"\n示例页面分词结果：\nURL: {sample_url}")
    print(f"精确分词：{crawler.segmented_content[sample_url]}")

# 统计总词语数（包括空格）
total_words = sum(len(words) for words in crawler.segmented_content.values())
print(f"\n总词语数：{total_words}")