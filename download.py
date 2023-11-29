from selenium import webdriver
from selenium.webdriver.common.by import By
import time  
import urllib
from slugify import slugify
import requests
import random
import os
import re
from multiprocessing import Pool
from threading import Thread

from retrieve_titles_urls_from_websites import *
import paperutils

# chromedriver_path = r'./supports/msedgedriver.exe'.replace('\\', '/')  # the chromedriver.exe path
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0'}


# 下载一个论文
def download_one(i, pdfname, pdfurl, root):
    if pdfurl != None:
        pdfname_slugified = slugify(pdfname, lowercase=False, separator="_")
        if os.path.isfile(root + '/' + pdfname_slugified + ".pdf"):
            print('existed', i, '\t', pdfname, '\t', pdfurl)
        else:
            print(i, '\t', pdfname, '\t', pdfurl)
            try_download = True
            while try_download:
                try:
                    data = requests.get(pdfurl, timeout=80, headers=headers).content
                    try_download = False
                except TimeoutError as e:
                    _ = time.sleep(random.uniform(1, 2))  # for anti-anti-crawler purpose
                except ConnectionError as e:
                    _ = time.sleep(random.uniform(1, 2))  # for anti-anti-crawler purpose
                except requests.exceptions.SSLError:
                    _ = time.sleep(random.uniform(1, 2))  # for anti-anti-crawler purpose
                except requests.exceptions.ProxyError:
                    _ = time.sleep(random.uniform(1, 2))  # for anti-anti-crawler purpose

            with open(root + '/' + pdfname_slugified + ".pdf", 'wb') as f:
                f.write(data)


def download_papers(conference, year, conference_url, subjcet,
                    patterns, root, statistics_root, num_threads):
    # 创建文件夹并打开浏览器 -- 可选Chrome或者Edge浏览器
    os.makedirs(root, exist_ok=True)
    os.makedirs(statistics_root, exist_ok=True)
    print(root)
    # get url of the conference
    driver = webdriver.Edge()  # 使用Edge浏览器
    # driver = webdriver.Chrome()         # 使用Chrome浏览器
    driver.get(conference_url)  # 连接一下

    # 获取全部论文
    pdfnamelist, pdfurllist = paperutils.get_all_papers(driver, conference, year, statistics_root)
    print("The Number of Paper ALL: ", len(pdfurllist))

    # 下载并保存当前主题的论文数据
    download_pdfnamelist, download_pdfurllist = paperutils.get_download_papers(pdfnamelist, pdfurllist,
                                                                               patterns=patterns)
    download_filename = conference + year + "_" + subjcet  # 保存到excel的文件名
    paperutils.save_papers_info(download_pdfnamelist, download_pdfurllist, statistics_root, download_filename)
    print("Total paper number in " + subjcet + " is: " + str(len(download_pdfurllist)))
    # 检查是否是我们要下载的论文    check the retrieved urls
    paperutils.check_download_papers(download_pdfnamelist, download_pdfurllist)

    # 下载论文
    print('The number of papers to download is ', len(download_pdfnamelist))
    assert len(download_pdfnamelist) == len(download_pdfurllist), 'Download Error: The number of titles and the number of urls are not matched. \
                                                    You might solve the problem by checking the HTML code in the \
                                                    website yourself or you could ask the author by raising an issue.'
    # download the papers one by one. The files are named after the titles (guaranteed to be valid file name after processed by slugify.)
    print('Start downloading')
    input_args = []
    for i, (pdfname, pdfurl) in enumerate(zip(download_pdfnamelist, download_pdfurllist)):
        input_args.append((i, pdfname, pdfurl, root))

    # 多线程下载
    with Pool(num_threads) as p:
        p.starmap(download_one, input_args)


if __name__ == '__main__':
    """
    some variables needed to be set up by users

    conference urls examples:
    ICCV: https://openaccess.thecvf.com/ICCV2023?day=all (ICCV 2023)
    CVPR: https://openaccess.thecvf.com/CVPR2021?day=all (CVPR 2021)
    ECCV: https://www.ecva.net/papers.php (ECCV 2020) (changed in 2020)
    CVPR: https://openaccess.thecvf.com/CVPR2020 (CVPR before 2020)
    NIPS: https://papers.nips.cc/paper/2020 (NeurIPS 2020)
    ICML: http://proceedings.mlr.press/v119/ (ICML 2020)
    ICLR: https://openreview.net/group?id=ICLR.cc/2021/Conference (ICLR 2021)
    Blow are not tested, may need some modify in retrieve_titles_urls_from_websites.py
    siggraph: https://dl.acm.org/toc/tog/2020/39/4 (SIGGRAPH 2021)

    """
    # 设置变量 variables to be set
    conference = 'CVPR'                                             # 会议名称, 小写
    year = "2023"                                                   # 年份
    conference_url = "https://openaccess.thecvf.com/CVPR2023?day=all"   # the conference url to download papers from
    subjcet = "Detect"                                              # 论文主题
    patterns = ["Detect", "DETR", "RCNN", "R-CNN", "YOLO"]          # 要检测的关键字, 全下载则不填: patterns = []
    root = (r'D:\Papers\CVPR2023_' + subjcet).replace('\\', '/')    # 设置本次下载的目录
    statistics_root = os.path.join(root, "statistics")              # 存放统计信息（图表）目录
    num_threads = 8                                                 # 进程数

    # run download
    download_papers(conference, year, conference_url, subjcet, patterns,
                    root, statistics_root, num_threads)


