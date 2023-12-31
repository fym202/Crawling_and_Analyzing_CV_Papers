# -*- coding: utf-8 -*-
"""
Created on 2023-11-21 14:46

@author: Fan yi ming

Func: 分析论文数据
"""
import os
import pandas as pd
from PIL import Image
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from collections import Counter
import numpy as np


# 从excel中读取论文标题并处理
def load_paper_title_from_excel(paper_root):
    # 读取文件
    text = ""
    if os.path.exists(paper_root):
        print('Loading information from ' + paper_root)
        papers_info = pd.read_excel(paper_root)
        columns = papers_info.columns  # 列分别为 No, PaperName, URL
        pdfnamelist = list(papers_info[columns[1]])
        # 处理成连续文本
        text = " ".join(pdfnamelist)
    else:
        print("Can not find excel: " + paper_root)
    return text


# 获取论文标题并预处理
def get_title_text(paper_list_roots, save_hyphen=True, trans_lower=True):
    """
    paper_list_root: excel表格的位置
    save_hyphen: 是否保留 - 符号，论文名字中的-常常是有用的
    trans_lower: 是否转换成小写，最好转换成小写。
    """
    text_list = []              # 全部文档中的text列表
    # 从列表中读取每个excel
    for paper_root in paper_list_roots:
        text_tmp = load_paper_title_from_excel(paper_root)
        text_list.append(text_tmp)
    text = " ".join(text_list)
    # 将文本转换为小写
    if trans_lower:
        text = text.lower()
    # 移除标点符号
    if save_hyphen:
        for ch in '''!"$%&()*+,./;:<=>?@[\\]^_{|}~''\n\t ''':
            text = text.replace(ch, " ")
    else:
        for ch in '''!"$%&()*+,-./;:<=>?@[\\]^_{|}~''\n\t ''':
            text = text.replace(ch, " ")
    return text


# 加载停止词, 找不到则不考虑停止词
def load_stop_words(stop_words_root):
    if os.path.exists(stop_words_root):
        with open(stop_words_root, encoding="utf-8") as f:
            stop_words = f.read().split()
    else:
        print("Can not find stop words.")
        stop_words = []
    return stop_words


# 去除掉统计中的停止词
def drop_stop_words(word_counts, stop_words):
    for word in stop_words:  # 去掉停用词
        word_counts.pop(word, 0)


# 统计论文标题的词频
def paper_title_word_frequency(paper_list_roots, stop_words_root=None):
    text = get_title_text(paper_list_roots)
    words = text.split()                 # 什么都不填表示用空格来分隔
    # 使用 Counter 统计单词出现的次数
    word_counts = Counter(words)
    # 去掉停止词
    stop_words = load_stop_words(stop_words_root)
    drop_stop_words(word_counts, stop_words)
    # 排序 - 转成一个字典
    sorted_frequencies = dict(sorted(word_counts.items(), key=lambda item: item[1], reverse=True))

    return sorted_frequencies


# 将词频信息保存到excel中
def save_word_frequency(frequencies, save_root, filename):
    df = pd.DataFrame(list(frequencies.items()), columns=['Word', 'Frequency'])
    if filename[-5:] != ".xlsx":
        filename = filename + ".xlsx"
    save_filename = os.path.join(save_root, filename)
    df.to_excel(save_filename, index=False)


# 绘制词云图
def generate_wordcloud(word_count, save_root, wordcloud_filename):
    # 加载背景图 -- 可以让词云更美观，但是不太适合论文中词语的显示
    # img = Image.open("./supports/background.png")  # 打开图片
    # img_array = np.array(img)  # 将图片装换为数组
    # wordcloud = WordCloud(width=800, height=400, background_color='white', mask=img_array)
    wordcloud = WordCloud(width=1600, height=1600, background_color='white')
    wordcloud == wordcloud.generate_from_frequencies(word_count)

    plt.figure(figsize=(10, 10))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    if wordcloud_filename[-4:] != ".png" and wordcloud_filename[-4:] != ".jpg":
        cloud_title = wordcloud_filename
    else:
        cloud_title = wordcloud_filename[:-4]
    plt.title(cloud_title, fontsize=20)
    # 默认保存.jpg
    if wordcloud_filename[-4:] != ".png" and wordcloud_filename[-4:] != ".jpg":
        wordcloud_filename = wordcloud_filename + ".jpg"
    # 图片显示和保存
    plt.savefig(os.path.join(save_root, wordcloud_filename), dpi=600)
    plt.show()


# 生成直方图
def generate_frequency_bar(word_frequency, show_num=20):
    word_freq = np.array(list(word_frequency.items()))[:show_num]
    words_x = word_freq[:, 0]
    freq_y = word_freq[:, 1].astype(int)
    # plot
    fig, ax = plt.subplots(figsize=(15, 10))

    # 条形图
    ax.bar(words_x, freq_y, width=1, edgecolor="white", linewidth=0.7)
    # 添加注释
    for a, b in zip(range(len(words_x)), freq_y):
        plt.text(a, b + 5, b, ha='center', va='bottom')
    ax.set(xlim=(-1, show_num), xticks=words_x)
    fig.autofmt_xdate()         # 自动旋转xlabel
    ax.set_title(f"Top {show_num} Frequency Word")


# 进行词频统计，绘图以及保存
def count_word_frequency(paper_list_roots, stop_words_root, save_root,
                         frequencies_filename, wordcloud_filename,
                         plot_wordcloud=True):
    # 进行词频统计
    frequency = paper_title_word_frequency(paper_list_roots, stop_words_root)
    print("\nTop 20 high-frequency words in paper titles.\n")
    print(list(frequency.items())[:20])
    # 保存词频到excel中
    save_word_frequency(frequency, save_root, frequencies_filename)
    # 绘制直方图
    generate_frequency_bar(frequency, 20)
    # 绘制词云图
    if plot_wordcloud:
        generate_wordcloud(frequency, save_root, wordcloud_filename)


# 得到单词的排名
def get_rank(word_freq, rank_cut = 200):
    ranks = np.empty_like(word_freq)
    ranks[0] = 1        # 最前面的排第一
    temp_rank = 1
    for i in range(1, word_freq.shape[0]):
        if word_freq[i-1] == word_freq[i]:
            ranks[i] = temp_rank
        else:
            temp_rank = i + 1
            if temp_rank >= 200:
                ranks[i:-1] = 200
                return ranks
            ranks[i] = temp_rank
    return ranks


# 存储到字典中
def store_ranks(words, ranks):
    save_dict = {}
    for word, rank in zip(words, ranks):
        save_dict[word] = rank
    return save_dict


# 保存排名变化到excel文件中
def save_rank_change(words, pre_post_rank, post_rank, rank_change,
                     save_root, filename):
    """
    words: 单词
    pre_post_rank: 单词对应的上一次的排面
    post_rank: 单词对应本次的排名
    rank_change: 单词本次相比上一次的变化
    """
    change_dict = {
        "Word": words,
        "PreRank": pre_post_rank,
        "PostRank": post_rank,
        "Change": rank_change
    }
    df = pd.DataFrame(change_dict)
    if filename[-5:] != ".xlsx":
        filename = filename + ".xlsx"
    save_filename = os.path.join(save_root, filename)
    print("Result of this compare save: " + save_filename)
    df.to_excel(save_filename, index=False)


# 对比前后的单词排名变化，从而得到趋势
def compare_word_rank(file_pre, file_post, save_root, save_name):
    print("Processing files: " + file_pre + "  and  " + file_post)
    # 输入为两个词频表
    word_freq_pre = pd.read_excel(file_pre)
    word_freq_post = pd.read_excel(file_post)
    # 获取rank
    rank_cut = 200
    pre_rank = get_rank(word_freq_pre['Frequency'], rank_cut)
    post_rank = get_rank(word_freq_post['Frequency'], rank_cut)
    # 转为字典
    pre_rank_dict = store_ranks(word_freq_pre['Word'], pre_rank)
    post_rank_dick = store_ranks(word_freq_post['Word'], post_rank)

    # 从200以后截断，只考虑前两百
    pre_PostRank = []               # 后面文件单词对应文件中的rank
    rank_changeList = []            # rank的变化
    dictkeys = list(post_rank_dick.keys())[:rank_cut]   # 只计算前rank_cut个数据的变化
    for word in dictkeys:
        pre_word_rank = pre_rank_dict.get(word)         # pre_rank, post_rank变量和之前的不同了
        if pre_word_rank is None:
            pre_word_rank = rank_cut
        pre_PostRank.append(pre_word_rank)
        post_word_rank = post_rank_dick.get(word)
        rank_change = pre_word_rank - post_word_rank
        rank_changeList.append(rank_change)
    # 保存到文件中
    save_rank_change(dictkeys, pre_PostRank, post_rank[:rank_cut], rank_changeList,
                     save_root, save_name)


if __name__ == '__main__':
    count_frequency_flag = True
    paper_list_roots = ["D:\Papers\ECCV2022_Detect\statistics\eccv2022_all.xlsx",
                       "D:\Papers\CVPR2022_Detect\statistics\cvpr2022_all.xlsx"]          # 根目录
    # parameters for 词频统计
    stop_words_root = "./supports/stop_words.txt"               # 停止词, 没有可以不填
    save_root = "D:\Papers\statistics"                          # 词频和图片保存路径
    frequencies_filename = "ALL_CV2022WordFrequency.xlsx"       # 保存词频的文件名
    wordcloud_filename = "ALL_CV2022_Word_Cloud"                # 保存词云图的文件名

    # 统计词频并绘图
    if count_frequency_flag:
        count_word_frequency(paper_list_roots, stop_words_root, save_root,
                             frequencies_filename, wordcloud_filename)

    # 比较前后变化
    word_rank_flag = False
    WordFrequency_Files = ["D:\Papers\statistics\ALL_CV2022WordFrequency.xlsx",
                           "D:\Papers\statistics\ALL_CV2023WordFrequency.xlsx"]
    rank_compare_filename = "WordRankCompare2022To2023.xlsx"
    if word_rank_flag:
        compare_word_rank(WordFrequency_Files[0], WordFrequency_Files[1], save_root, rank_compare_filename)




