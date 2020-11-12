import requests
import time
import re
import argparse
import sys
import threading
import html
from requests_html import HTMLSession
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


skip_content_type = ['application/zip', 'application/octet-stream', 'application/msword', 'application/pdf']  # 过滤文件二进制
code_list = [500, 501, 502, 503, 504, 505, 401, 402, 400]  # 过滤不能访问的http状态

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.122 Safari/537.36'
}
skip_43 = [404, 403]

banner = '''
  _    _ _______ _______ _____   _____  _____          _   _ 
 | |  | |__   __|__   __|  __ \ / ____|/ ____|   /\   | \ | |
 | |__| |  | |     | |  | |__) | (___ | |       /  \  |  \| |
 |  __  |  | |     | |  |  ___/ \___ \| |      / /\ \ | . ` |
 | |  | |  | |     | |  | |     ____) | |____ / ____ \| |\  |
 |_|  |_|  |_|     |_|  |_|    |_____/ \_____/_/    \_\_| \_|
                                                 
                       ___v 1.0___            author:default                  
'''

title_list = []  # 标题
Content_Length_list = []  # 响应包长度


def requests_url(url):
    res = requests.get(url=url, timeout=15, headers=headers, verify=False)
    return res


# 获取url列表
def get_url(url_txt):
    with open(url_txt, "r")as f:
        s = f.readlines()
        lt = [i.strip() for i in s]
    return lt


# 发送请求验证


def process_data(lt, out_name, error_int, code_list, retry):
    # p_lt = []  # 最终结果列表
    # num = 0  # 测试url定位
    Response_error = error_int  # 响应包误差波动值

    for i in lt:
        # num += 1
        # print("正在测试第{}个url".format(num))

        try:

            r = requests_url(i)

            pattern = re.compile(r'window.top.location.href')
            search_str = pattern.search(r.text)

            if bool(search_str):
                pattern = re.compile(r'(?<=window\.top\.location\.href=")(.+?)(?=";</script>)')
                red_url = pattern.search(r.text).group()
                i = i + red_url
                r = requests_url(i)
            content_length = len(r.content)
            print('')
            print(r.status_code)
            # print(content_length)
            content_type = r.headers.get('content-type')

            if r.status_code not in code_list:
                if r.status_code in skip_43 and content_length not in Content_Length_list:  # 若想多搜集403or404资产建议关闭响应包筛选
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
                    r.encoding = 'UTF-8'
                    content = r.text
                    whether_title = bool(re.findall('<title>(.*)</title>', content))

                    if whether_title:
                        title = re.findall('<title>(.*)</title>', content)[0]
                        print(title)

                        if title not in title_list and content_length not in Content_Length_list:
                            title_list.append(title)

                            for error in range(Response_error + 1):
                                if error == 0:
                                    Content_Length_list.append(content_length)
                                else:
                                    Content_Length_list.append(content_length + error)
                                    Content_Length_list.append(content_length - error)
                            print("{}  可成功访问".format(i))

                            output_data(i, out_name)
                        else:
                            print("\033[31m repeat\033[0m")
                            continue
                    else:
                        if content_length not in Content_Length_list:

                            for error in range(Response_error + 1):
                                if error == 0:
                                    Content_Length_list.append(content_length)
                                else:
                                    Content_Length_list.append(content_length + error)
                                    Content_Length_list.append(content_length - error)
                            print("{}  可成功访问".format(i))

                            output_data(i, out_name)
                        else:
                            print("\033[31m repeat\033[0m")
                            continue



            else:
                print("{}  不能成功访问,响应码为{}".format(i, r.status_code))
                print('')

                continue


        except:

            cs = retry  # 设置重连次数
            for c in range(cs):
                c += 1
                # time.sleep(0)
                if c == cs:
                    print('')
                    print("{}   访问超时".format(i))
                    output_data(i, '访问超时.txt')
                    continue

    return title_list, Content_Length_list


def output_data(i, out_name):
    with open(out_name, "a") as f:
        f.write(i + "\n")

    # print('')


def main():
    print(banner)
    parser = argparse.ArgumentParser(usage='python3 http_scan.py -u file.txt')
    parser.add_argument('-u', '--url', required=True, help='target url file')
    parser.add_argument('-c', '--code', required=False, type=int, nargs='+',
                        default=[500, 501, 502, 503, 504, 505, 401, 402, 400], help='skip status code')
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

    print('')
    print("可成功访问的url已保存在{}文件中.".format(out_name))
    sys.exit()


if __name__ == "__main__":
    main()
