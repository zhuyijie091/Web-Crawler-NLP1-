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

import math


class ShortestPathSegmenter:
    def __init__(self, dict_path):
        self.word_freq = {}  # 词频字典
        self.total_freq = 0  # 总词频
        self.max_word_len = 0  # 最大词长
        self.load_dict(dict_path)  # 加载词典

        if not self.word_freq:
            raise ValueError("词典加载失败，请检查词典文件")

    def load_dict(self, dict_path):
        """加载词典并计算词频"""
        with open(dict_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) < 2:
                    continue
                word, freq = parts[0], int(parts[1])
                if any('\u4e00' <= c <= '\u9fff' for c in word):
                    self.word_freq[word] = freq
                    self.total_freq += freq
                    self.max_word_len = max(self.max_word_len, len(word))

        # 计算默认未登录词权重（出现一次的概率）
        self.unknown_freq = 1
        self.total_freq += self.unknown_freq

    def calculate_weight(self, word):
        """计算词的权重（取负对数概率）"""
        freq = self.word_freq.get(word, self.unknown_freq)
        prob = freq / self.total_freq
        return -math.log(prob)  # 转化为最短路径问题

    def build_dag(self, sentence):
        """构建有向无环图(DAG)"""
        dag = {}
        length = len(sentence)

        for i in range(length):
            dag[i] = []
            # 允许单字词
            end = min(i + 1, length)
            dag[i].append(end)

            # 查找可能的长词
            max_end = min(i + self.max_word_len, length)
            for j in range(i + 2, max_end + 1):
                word = sentence[i:j]
                if word in self.word_freq:
                    dag[i].append(j)
        return dag

    def shortest_path(self, sentence):
        """动态规划计算最短路径"""
        length = len(sentence)
        dag = self.build_dag(sentence)

        # 初始化DP表
        dp = {0: (0.0, 0)}  # {位置: (累计权重, 前驱位置)}

        for i in range(length):
            if i not in dag:
                continue

            current_weight = dp[i][0] if i in dp else float('inf')

            for j in dag[i]:
                word = sentence[i:j]
                weight = self.calculate_weight(word)
                new_weight = current_weight + weight

                if j not in dp or new_weight < dp[j][0]:
                    dp[j] = (new_weight, i)

        # 回溯路径
        path = []
        end_pos = length
        while end_pos > 0:
            if end_pos not in dp:
                # 处理无法回溯的情况（未登录词）
                start_pos = max(0, end_pos - 1)
                path.append(start_pos)
                end_pos = start_pos
                continue

            start_pos = dp[end_pos][1]
            path.append(start_pos)
            end_pos = start_pos

        # 生成分词结果
        path = sorted(list(set(path)))
        result = []
        for i in range(1, len(path)):
            start = path[i - 1]
            end = path[i]
            result.append(sentence[start:end])

        # 处理最后一个词
        if path and path[-1] < length:
            result.append(sentence[path[-1]:])

        return result


# 使用示例
if __name__ == "__main__":
    # 初始化分词器
    segmenter = ShortestPathSegmenter('dictionary_sm.txt')

    for url, text in crawler.content.items():
        # 去除空格并分词（根据你的实际需求调整预处理）
        clean_text = text.replace(' ', '')
        seg_list = segmenter.shortest_path(clean_text)
        print(f"URL: {url}")
        print(f"分词结果: {'/'.join(seg_list[:50])}...")  # 只显示前50个分词结果
        print("----------")

