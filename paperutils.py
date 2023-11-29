# -*- coding: utf-8 -*-
"""
Created on 2023-11-19 9:45

@author: Fan yi ming

Func: utils of paper crawler

参数： 默认先Name 后 url
"""
import numpy as np
import pandas as pd
import re
import os

from retrieve_titles_urls_from_websites import *


# 获取会议中的全部论文, 并保存论文信息
def get_all_papers(driver, conference, year, statistics_root):
    pdfurllist, pdfnamelist = [], []
    filename = conference + year + "_all"      # 保存的文件名
    info_save_root = os.path.join(statistics_root, filename+".xlsx")  # 论文info保存的表格路径
    if os.path.exists(info_save_root):
        print('Loading pdf urls from excel. This could take little time...')
        papers_info = pd.read_excel(info_save_root)
        columns = papers_info.columns                # 列分别为 No, PaperName, URL
        pdfnamelist = list(papers_info[columns[1]])
        pdfurllist = list(papers_info[columns[2]])
    else:
        # get paper list
        retrieve = globals()['retrieve_from_'+conference]
        print('Retrieving pdf urls. This could take some time...')
        if conference in ["ECCV", "CVPR", "ICLR"]:
            pdfurllist, pdfnamelist = retrieve(driver, year)
        else:
            pdfurllist, pdfnamelist = retrieve(driver)
            # 防止爬取错误
        assert len(pdfnamelist) == len(pdfurllist), 'Web Crawler Error:The number of titles and the number of urls are not matched. \
                                                    You might solve the problem by checking the HTML code in the \
                                                    website yourself or you could ask the author by raising an issue.'
        if len(pdfurllist) > 0:   # 抓到则保存到文件中
            save_papers_info(pdfnamelist, pdfurllist, save_root=statistics_root, filename=filename)

    return pdfnamelist, pdfurllist


# 根据主题筛选要下载的论文
def get_download_papers(pdfnamelist, pdfurllist, patterns):
    # 下载全部文件
    if len(patterns) == 0:
        return pdfnamelist, pdfurllist

    download_pdfurllist = []
    download_pdfnamelist = []
    # 筛选包含关键词的论文
    for i in range(len(pdfnamelist)):
        download_flag = False  # 判断是否下载的变量
        for p in patterns:
            if re.search(p, pdfnamelist[i]):  # 检索到关键词就设置True并跳出
                download_flag = True
                break
        # flag为 True 就下载
        if download_flag:
            download_pdfurllist.append(pdfurllist[i])
            download_pdfnamelist.append(pdfnamelist[i])
    return download_pdfnamelist, download_pdfurllist


# 查看和检查要下载的文件
def check_download_papers(download_pdfnamelist, download_pdfurllist):
    # check the retrieved urls
    print('The first 5 pdf urls:\n')
    for i in range(min(5, len(download_pdfurllist))):
        print(download_pdfurllist[i])
    print('\nThe last 5 pdf urls:\n')
    for i in range(min(5, len(download_pdfurllist))):
        print(download_pdfurllist[-(i + 1)])
    print('=======================================================')
    # check the retrieved paper titles
    print('The first 5 pdf titles:\n')
    for i in range(min(5, len(download_pdfnamelist))):
        print(download_pdfnamelist[i])
    print('\nThe last 5 pdf titles:\n')
    for i in range(min(5, len(download_pdfnamelist))):
        print(download_pdfnamelist[-(i + 1)])


# 将论文信息保存到excel中
def save_papers_info(pdfnamelist, pdfurllist, save_root, filename):
    df = pd.DataFrame({
        "No": np.array(range(len(pdfnamelist))),
        "PaperName": pdfnamelist,
        "URL": pdfurllist
    })
    if filename[-5:] != ".xlsx":
        filename = filename + ".xlsx"
    save_filename = os.path.join(save_root, filename)
    df.to_excel(save_filename, index=False)


if __name__ == '__main__':
    pdfnamelist = ["1", "2", "3"]
    pdfurllist = ["1", "2", "3"]
    subject = "Detect"
    root = (r'D:\Papers\NIPS2022_' + subject).replace('\\', '/')  # 设置本次下载的目录
    statistics_root = os.path.join(root, "statistics")  # 存放统计信息（图表）

    save_papers_info(pdfnamelist, pdfurllist, save_root=statistics_root, filename="test")
