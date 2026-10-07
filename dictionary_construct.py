# ##只包含词的构建方法
# # 打开输入文件并读取内容
# input_file = 'dict.txt.small'  # 输入文件名
# output_file = 'dictionary.txt'  # 输出文件名
#
# try:
#     with open(input_file, 'r', encoding='utf-8') as infile:
#         lines = infile.readlines()
#
#     # 提取左边的词
#     words = []
#     for line in lines:
#         # 假设每行的格式是“词 数字 字母”，通过空格分割
#         parts = line.strip().split()
#         if parts:  # 确保行不为空
#             word = parts[0]  # 第一个部分是词
#             words.append(word)
#
#     # 将提取的词写入输出文件
#     with open(output_file, 'w', encoding='utf-8') as outfile:
#         for word in words:
#             outfile.write(word + '\n')
#
#     print(f"提取完成！字典已保存到 {output_file}")
#
# except FileNotFoundError:
#     print(f"错误：文件 {input_file} 未找到，请检查文件路径是否正确。")
# except Exception as e:
#     print(f"发生错误：{e}")


# ##包含词和词频的构建
#
# # 打开输入文件并读取内容
# input_file = 'dict.txt.small'  # 输入文件名
# output_file = 'dictionary_sm.txt'  # 输出文件名
#
# try:
#     with open(input_file, 'r', encoding='utf-8') as infile:
#         lines = infile.readlines()
#
#     # 提取前两列的词
#     extracted_content = []
#     for line in lines:
#         # 假设每行的格式是“词 数字 字母”，通过空格分割
#         parts = line.strip().split()
#         if len(parts) >= 2:  # 确保行中有足够的部分
#             word = parts[0]  # 第一个部分是词
#             number = parts[1]  # 第二个部分是数字
#             extracted_content.append(f"{word} {number}")  # 将前两列内容组合
#
#     # 将提取的内容写入输出文件
#     with open(output_file, 'w', encoding='utf-8') as outfile:
#         for content in extracted_content:
#             outfile.write(content + '\n')
#
#     print(f"提取完成！内容已保存到 {output_file}")
#
# except FileNotFoundError:
#     print(f"错误：文件 {input_file} 未找到，请检查文件路径是否正确。")
# except Exception as e:
#     print(f"发生错误：{e}")

##带有词和标签的词典构建

