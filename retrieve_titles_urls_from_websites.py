import re
import time

from selenium.webdriver.common.by import By


# def retrieve_from_siggraph(driver):
#     pdfurllist =  []
#     pdfnamelist = []
#     import time    
#     elementllist =  driver.find_elements_by_class_name('toc__section')[1:-2]
#     for i, section in enumerate(elementllist):
#         section.find_element_by_partial_link_text('SESSION').click()
#         time.sleep(3)
#         # print(session_name)
#         for j, paper_element in enumerate(section.find_elements_by_class_name('issue-item__content')):
#             paper_name = paper_element.find_element_by_xpath('div/h5').text
#             pdf_url = paper_element.find_element_by_class_name('red').get_attribute('href')

#             pdfnamelist.append(paper_name)
#             pdfurllist.append(pdf_url)

#     return pdfurllist, pdfnamelist


def retrieve_from_siggraph(driver):
    pdfurllist = []
    pdfnamelist = []
    import time
    elementllist = driver.find_elements_by_class_name('accordion-tabbed')[1].find_elements_by_class_name('toc__section')
    for i, section in enumerate(elementllist):
        section.click()
        time.sleep(3)
        print('\n', section.text)
        for j, paper_element in enumerate(section.find_elements_by_class_name('issue-item__content')):
            paper_name = paper_element.find_element_by_xpath('div/h5').text
            pdf_url = paper_element.find_element_by_class_name('red').get_attribute('href')
            print('\t', paper_name)
            pdfnamelist.append(paper_name)
            pdfurllist.append(pdf_url)

    return pdfurllist, pdfnamelist


# ICLR, 实现的并不好，可以考虑把总页数提取出来，for循环实现
def retrieve_from_ICLR(driver, year):
    pdfurllist = []
    pdfnamelist = []
    if int(year) == 2022:         # 2022
        # three sections: oral, spotlight, poster
        sections = ['Oral', 'Spotlight', 'Poster']
        web_ids = ['oral-submissions', 'spotlight-submissions', 'poster-submissions']
    elif int(year) <= 2021:
        # three sections: oral, spotlight, poster
        sections = ['Oral', 'Spotlight', 'Poster']
        web_ids = ['oral-presentations', 'spotlight-presentations', 'poster-presentations']
    else:                       # 2023
        # three sections: Notable-top-5, Notable-top-5, poster
        sections = ['Notable-top-5', 'Notable-top-25', 'Poster']
        web_ids = ['notable-top-5-', 'notable-top-25-', 'poster']
    time.sleep(10)               # 等待5s，让页面加载一会
    for s_num, section in enumerate(sections):                # each section
        section_chose = driver.find_element(by=By.PARTIAL_LINK_TEXT, value=section)
        driver.execute_script("arguments[0].click();", section_chose)
        time.sleep(2)                   # 等待2s，让页面加载一会
        find_next = True                # 是否存在下一页,2022以后会分页
        if int(year) >= 2022:           # 2022之后
            while find_next:
                section_element = driver.find_element(by=By.ID, value=web_ids[s_num])
                elementllist = section_element.find_elements(by=By.TAG_NAME, value='h4')[1:]
                for i, element in enumerate(elementllist):
                    pdfnamelist.append(elementllist[i].text)
                    pdfurllist.append(elementllist[i].find_elements(by=By.XPATH, value='a')[1].get_attribute('href'))
                # 寻找下一页
                page_container = driver.find_elements(by=By.CLASS_NAME, value="pagination")
                page_elements = page_container[s_num].find_elements(by=By.XPATH, value="li")   # 所有li元素
                # 这里用find_elements找到下一页标签中跳转链接，如果得到的是空，则表示没有下一页
                next_page = page_elements[-2].find_elements(by=By.XPATH, value='a')             # 找到并判断是否存在下一页
                if len(next_page) > 0:                                                         # 持续点击下一页 >
                    driver.execute_script("arguments[0].click();", next_page[0])
                    time.sleep(2)
                else:
                    find_next = False
        else:                           # 2022之前
            section_element = driver.find_element(by=By.ID, value=web_ids[s_num])
            elementllist = section_element.find_elements(by=By.TAG_NAME, value='h4')[1:]
            for i, element in enumerate(elementllist):
                pdfnamelist.append(elementllist[i].text)
                pdfurllist.append(elementllist[i].find_elements(by=By.XPATH, value='a')[1].get_attribute('href'))

    return pdfurllist, pdfnamelist


def retrieve_from_ICML(driver):
    pdfurllist = []
    pdfnamelist = []
    elementllist = driver.find_elements(by=By.CLASS_NAME, value='title')
    url_element_list = driver.find_elements(by=By.LINK_TEXT, value='Download PDF')
    for i, element in enumerate(url_element_list):
        pdfnamelist.append(elementllist[i].text)
        pdfurllist.append(url_element_list[i].get_attribute('href'))
    return pdfurllist, pdfnamelist


def retrieve_from_NIPS(driver):
    pdfurllist = []
    pdfnamelist = []
    elementllist = driver.find_elements(by=By.TAG_NAME, value='li')[2:]
    for i, element in enumerate(elementllist):
        pdfnamelist.append(elementllist[i].find_elements(by=By.XPATH, value='a')[0].text)
        pdfurllist.append(
            elementllist[i].find_elements(by=By.XPATH, value='a')[0].get_attribute('href').replace('hash', 'file', 1). \
            replace('Abstract.html', 'Paper.pdf', 1))
    return pdfurllist, pdfnamelist


def retrieve_from_CVPR(driver, year):
    pdfurllist = []
    pdfnamelist = []
    if int(year) > 2020:  # 2020年以后
        title_element_list = driver.find_elements(by=By.CLASS_NAME, value='ptitle')
        url_element_list = driver.find_elements(by=By.PARTIAL_LINK_TEXT, value='pdf')
        for i, element in enumerate(url_element_list):
            pdfnamelist.append(title_element_list[i].text)
            pdfurllist.append(url_element_list[i].get_attribute('href'))
    else:  # 2020年之前
        for day in range(3):
            driver.find_elements(by=By.XPATH, value='//body/div[3]/dl/dd/a')[day].click()
            title_element_list = driver.find_elements(by=By.CLASS_NAME, value='ptitle')
            url_element_list = driver.find_elements(by=By.PARTIAL_LINK_TEXT, value='pdf')
            for i, element in enumerate(url_element_list):
                pdfnamelist.append(title_element_list[i].text)
                pdfurllist.append(url_element_list[i].get_attribute('href'))
            driver.back()
    return pdfurllist, pdfnamelist


def retrieve_from_ICCV(driver):
    pdfurllist = []
    pdfnamelist = []

    title_element_list = driver.find_elements(by=By.CLASS_NAME, value='ptitle')
    url_element_list = driver.find_elements(by=By.PARTIAL_LINK_TEXT, value='pdf')
    for i, element in enumerate(url_element_list):
        pdfnamelist.append(title_element_list[i].text)
        pdfurllist.append(url_element_list[i].get_attribute('href'))
    return pdfurllist, pdfnamelist


def retrieve_from_ECCV(driver, year):
    pdfurllist = []
    pdfnamelist = []

    # 需要click一下按钮才能下载
    button_element = driver.find_elements(by=By.CLASS_NAME, value='accordion')
    pattern = str(year)
    # 点击对应年份的按钮
    time.sleep(2)  # 等待2s，让页面加载一会
    for i, element in enumerate(button_element):
        if re.search(pattern, element.text):
            driver.execute_script("arguments[0].click();", element)
            time.sleep(2)
            break
    # 找到论文和连接列表
    elementllist = driver.find_elements(by=By.CLASS_NAME, value='ptitle')
    url_element_list = driver.find_elements(by=By.PARTIAL_LINK_TEXT, value='pdf')
    # 找到论文的题目
    for i, element in enumerate(elementllist):
        if len(element.text) > 0:
            pdfnamelist.append(element.text)
    # 找论文url
    for i, element in enumerate(url_element_list):
        pdfurllist.append(url_element_list[i].get_attribute('href'))
    return pdfurllist, pdfnamelist
