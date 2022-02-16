import requests
import asyncio, time
import re
import argparse
import sys
import threading
from requests_html import AsyncHTMLSession, HTMLSession
import urllib3
import openpyxl
from pyppeteer import launch

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


skip_content_type = ['application/zip', 'application/octet-stream', 'application/msword', 'application/pdf']  # 过滤文件二进制
code_list = [500, 501, 502, 503, 504, 505]  # 过滤不能访问的http状态

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:84.0) Gecko/20100101 Firefox/84.0'
}
skip_43 = [404, 403, 401, 410, 400]


banner = '''
           _                         
  _    _ _______ _______ _____   _____  _____          _   _ 
 | |  | |__   __|__   __|  __ \ / ____|/ ____|   /\   | \ | |
 | |__| |  | |     | |  | |__) | (___ | |       /  \  |  \| |
 |  __  |  | |     | |  |  ___/ \___ \| |      / /\ \ | . ` |
 | |  | |  | |     | |  | |     ____) | |____ / ____ \| |\  |
 |_|  |_|  |_|     |_|  |_|    |_____/ \_____/_/    \_\_| \_|
                                                 
                       ___v 1.3___            author:default                    
'''



# 获取url列表
def get_url(url_txt):

    with open(url_txt, "r")as f:
        s = f.readlines()
        lt = [i.strip() for i in s]
    return lt


# 发送请求验证
list = []
title_list = []  # 标题
Content_Length_list = []  # 响应包长度
session = HTMLSession(verify=False)
def process_data(lt, out_name, error_int, code_list, retry):
    # p_lt = []  # 最终结果列表
    # num = 0  # 测试url定位
    Response_error = error_int  # 响应包误差波动值 /默认关闭


    for i in lt:


        try:

            r = session.get(url=i, timeout=30, headers=headers,verify=False)

            content_length = len(r.content)
            print('')
            print(r.status_code)
            # print(content_length)
            content_type = str(r.headers.get('content-type'))

            if r.status_code not in code_list:
                if r.status_code in skip_43:   # 若想多搜集403or404资产建议关闭响应包筛选and content_length not in Content_Length_list:
                    for error in range(Response_error + 1):
                        if error == 0:
                            Content_Length_list.append(content_length)
                        else:
                            Content_Length_list.append(content_length + error)
                            Content_Length_list.append(content_length - error)
                    print("{}  可成功访问".format(i))
                    output_data(i, '403_4.txt')
                    continue

                elif content_length > 2000000 or content_type in skip_content_type or bool(
                        re.search('text/plain', content_type)):
                    output_data(i, '下载连接or纯文本.txt')
                    print("{}   可成功访问，该url为下载连接or纯文本".format(i))

                elif r.status_code not in code_list:
                    r.encoding = r.apparent_encoding

                    content = r.text.replace('\r', '').replace('\n', '').replace(' ', '')

                    whether_title = bool(re.findall(r"(?<=><title>)(.+?)(?=</title>)", content))
                    whether_title2 = bool(re.findall(r"(?<=<title>)(.+?)(?=</title>)", content))
                    
                    if whether_title or whether_title2:
                        if whether_title:
                            title = re.findall('(?<=><title>)(.+?)(?=</title>)', content)[0]
                            if title == '':
                                output_data(i, 'kong_title.txt')
                        if whether_title2:
                            title = re.findall('(?<=<title>)(.+?)(?=</title>)', content)[0]
                    if content_length ==0:
                        output_data(i,'kong_page.txt')
                        continue
                    if bool(r.html.find('title', first=True)):
                        title = r.html.find('title', first=True).text
                        if title == '':
                            output_data(i, 'kong_title.txt')
                            continue
                        print(title)
                        # print(title_list)
                        reg = "Not Found|Apache Tomcat|IIS Windows Server|IIS7|IIS|Tomcat|Welcome"
                        skip_title = "CDN|DNS"
                        flag = bool(re.findall(reg, title))
                        flag_skip = bool(re.findall(skip_title, title))
                        if flag and flag_skip==False:
                            output_data(i+'      '+title, '中间件首页.txt')
                            continue

                        # or content_length not in Content_Length_list
                        if title not in title_list:
                            title_list.append(title)
                            for error in range(Response_error + 1):
                                if error == 0:
                                    Content_Length_list.append(content_length)
                                else:
                                    Content_Length_list.append(content_length + error)
                                    Content_Length_list.append(content_length - error)
                            print("{}  可成功访问".format(i))
                            x_list = []
                            x_list.append(i)
                            x_list.append(title)

                            list.append(x_list)

                            output_data(i+'      '+title, out_name)

                        else:
                            print("\033[31m repeat\033[0m")
                            output_data(i+'      '+title, 'repeat.txt')
                            continue
                    else:

                        #写入检测是否需要执行js跳转，windows.location
                        output_data(i, '改url未检索到标题.txt')
                        continue


            else:


                print("{}  不能成功访问,响应码为{}".format(i, r.status_code))
                output_data(i, '50x.txt')
                print('')
                continue


        except:
            output_data(i, '访问超时.txt')
            print("{}   访问超时".format(i))
            time.sleep(0)
            continue


    return title_list, Content_Length_list,list


def output_data(i, out_name):
    with open(out_name, "a", encoding='utf-8') as f:
        f.write(i + "\n")

def write_excel_xlsx(path, sheet_name, value):
    index = len(value)
    workbook = openpyxl.Workbook()  # 新建工作簿（默认有一个sheet？）
    sheet = workbook.active  # 获得当前活跃的工作页，默认为第一个工作页
    sheet.column_dimensions['A'].width = 50.0
    sheet.column_dimensions['B'].width = 40.0
    sheet.title = sheet_name  # 给sheet页的title赋值
    for i in range(0, index):
        for j in range(0, len(value[i])):
            sheet.cell(row=i + 1, column=j + 1, value=str(value[i][j]))  # 行，列，值 这里是从1开始计数的
    workbook.save(path)  # 一定要保存


def main():
    #start = time.perf_counter()
    print(banner)
    parser = argparse.ArgumentParser(usage='python3 http_scan.py -u file.txt')
    parser.add_argument('-u', '--url', required=True, help='target url file')
    parser.add_argument('-c', '--code', required=False, type=int, nargs='+',
                        default=[500, 501, 502, 503, 504, 505, 402, 405], help='skip status code')
    parser.add_argument('-e', '--error', required=False, type=int, default=1, help='response packet error')
    parser.add_argument('-r', '--retry', required=False, type=int, default=1, help='Timeout reconnection')
    parser.add_argument('-t', '--Threads', required=False, type=int, default=1, help='number of threads,default = 1')
    parser.add_argument('-o', '--output', required=False, default='url_out.txt', help='result')
    args = parser.parse_args()
    url_txt = args.url
    out_name = args.output
    error_int = args.error
    code_list = args.code
    retry = args.retry
    numbers = args.Threads
    lt = get_url(url_txt)


    thread_list = []
    thflist = [[] for i in range(numbers)]
    for i, e in enumerate(lt):
        thflist[i % numbers].append(e)
    for i in thflist:
        thread_list.append(i)
    # print(thread_list)

    thread_list = [threading.Thread(target=process_data, args=(thread_list[i], out_name, error_int, code_list, retry))
                   for i in range(len(thread_list))]
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()

    #end = time.perf_counter()
    #print('运行时间 : %s 秒' % (end - start))
    print('')
    write_excel_xlsx('url_out.xlsx', 'result', list)
    print("可成功访问的url已保存在url_out.xlsx文件中")
    sys.exit()


if __name__ == "__main__":
    main()
