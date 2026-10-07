import numpy as np
from collections import defaultdict
import os


class HMMSegmentation:
    def __init__(self):
        self.states = ['B', 'M', 'E', 'S']
        self.state2id = {s: i for i, s in enumerate(self.states)}
        self.init_prob = np.zeros(4)
        self.trans_prob = np.zeros((4, 4))
        self.emit_prob = defaultdict(lambda: np.zeros(4))
        self.vocab = set()

    def train(self, sentences):
        init_counts = np.ones(4)  # 加一平滑
        trans_counts = np.ones((4, 4))
        emit_counts = defaultdict(lambda: np.ones(4))

        for sentence in sentences:
            _, tags = self._get_tags(sentence)
            init_counts[self.state2id[tags[0]]] += 1
            for i in range(len(tags) - 1):
                trans_counts[self.state2id[tags[i]], self.state2id[tags[i + 1]]] += 1
            for char, tag in zip(''.join(sentence), tags):
                emit_counts[char][self.state2id[tag]] += 1
                self.vocab.add(char)

        # 转换为对数概率
        self.init_prob = np.log(init_counts / init_counts.sum())
        self.trans_prob = np.log(trans_counts / trans_counts.sum(axis=1, keepdims=True))
        for char in emit_counts:
            total = emit_counts[char].sum()
            self.emit_prob[char] = np.log(emit_counts[char] / total)

    def _get_tags(self, words):
        tags = []
        for word in words:
            if len(word) == 1:
                tags.append('S')
            else:
                tags.append('B')
                tags.extend(['M'] * (len(word) - 2))
                tags.append('E')
        return list(''.join(words)), tags

    def _viterbi(self, sentence):
        chars = list(sentence)
        T = len(chars)
        viterbi = np.full((4, T), -np.inf)
        backpointers = np.zeros((4, T), dtype=int)

        # 初始化
        for s in range(4):
            emit = self.emit_prob[chars[0]][s] if chars[0] in self.vocab else -20
            viterbi[s, 0] = self.init_prob[s] + emit

        # 递推
        for t in range(1, T):
            for s in range(4):
                trans_scores = viterbi[:, t - 1] + self.trans_prob[:, s]
                max_score = np.max(trans_scores)
                backpointers[s, t] = np.argmax(trans_scores)
                emit = self.emit_prob[chars[t]][s] if chars[t] in self.vocab else -20
                viterbi[s, t] = max_score + emit

        # 回溯
        best_path = [np.argmax(viterbi[:, -1])]
        for t in range(T - 1, 0, -1):
            best_path.insert(0, backpointers[best_path[0], t])

        return [self.states[s] for s in best_path]

    def cut(self, sentence):
        tags = self._viterbi(sentence)
        result = []
        current_word = []
        for char, tag in zip(sentence, tags):
            current_word.append(char)
            if tag in ['S', 'E']:
                result.append(''.join(current_word))
                current_word = []
        if current_word:
            result.append(''.join(current_word))
        return result


def load_jieba_dict(filepath):
    """加载jieba词典文件（带词频和词性）"""
    sentences = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                word = line.split()[0]  # 提取词语部分
                sentences.append([word])
    return sentences


if __name__ == "__main__":
    hmm = HMMSegmentation()

    # 你的实际路径
    jieba_dict_path = r'C:\Users\wx280\.conda\envs\NLP\Lib\site-packages\jieba\dict.txt'

    # 路径验证
    if not os.path.isfile(jieba_dict_path):
        print(f"错误：词典文件不存在于以下路径\n{jieba_dict_path}")
        print("请检查：")
        print("1. 路径中的反斜杠是否正确转义")
        print("2. 是否实际存在该文件")
        print("3. 文件权限是否正常")
        exit()

    try:
        print("正在加载词典...")
        train_data = load_jieba_dict(jieba_dict_path)
        print(f"成功加载 {len(train_data)} 个词语")

        print("开始训练HMM模型...")
        hmm.train(train_data)
        print("训练完成！输入句子进行分词（输入exit退出）")
    except Exception as e:
        print(f"初始化失败：{str(e)}")
        exit()

    while True:
        try:
            text = input("\n请输入中文句子：").strip()
            if text.lower() in ['exit', 'quit']:
                break
            if not text:
                continue
            if any(ord(c) > 255 for c in text):  # 简单中文验证
                result = hmm.cut(text)
                print("分词结果：", " / ".join(result))
            else:
                print("请输入包含中文的句子")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"处理出错：{str(e)}")