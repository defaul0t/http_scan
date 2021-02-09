import requests_html
import urllib3
import time
import re
import argparse
import sys
import threading

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# text_url = 'https://www.baidu.com'
# user_agent = requests_html.user_agent()
# print("User-Agent：", user_agent)
# session = requests_html.HTMLSession()
# headers = {
#     "User-Agent": user_agent
# }
# r = session.get(text_url, headers=headers)
# r.html.render(sleep=3)
# node = r.html.find('title', first=True)
# print(node.text)

code_list = [500, 501, 502, 503, 504, 505, 401, 402, 400]  # 过滤不能访问的http状态
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8'
}
skip_43 = [404, 403]

banner = '''
  _    _ _______ _______ _____   _____  _____          _   _ 
 | |  | |__   __|__   __|  __ \ / ____|/ ____|   /\   | \ | |
 | |__| |  | |     | |  | |__) | (___ | |       /  \  |  \| |
 |  __  |  | |     | |  |  ___/ \___ \| |      / /\ \ | . ` |
 | |  | |  | |     | |  | |     ____) | |____ / ____ \| |\  |
 |_|  |_|  |_|     |_|  |_|    |_____/ \_____/_/    \_\_| \_|

                       ___v 2.0___            author:default                  
'''
skip_title = "高效|58盾|信息提示|汽车网|分类信息|安居客租房网|分类信息门户|乐享网|人才网|分类|二手车|车市|访问验证|天鹅到家|瓜子二手车直卖网|58汽车|驾校一点通" #关键字过滤

skip_content_type = ['application/zip', 'application/octet-stream', 'application/msword', 'application/pdf']  # 过滤文件二进制


def requests_url(url):
    session = requests_html.HTMLSession()
    r = session.get(url=url, headers=headers)

    return r
# r = requests_url(text_url)
# r.html.render(sleep=2)
# p = r.html.html
# print(p)

# 获取url列表
def get_url(url_txt):
    with open(url_txt, "r")as f:
        s = f.readlines()
        lt = [i.strip() for i in s]
    return lt


def output_data(i, out_name):
    with open(out_name, "a", encoding='utf-8') as f:
        f.write(i + "\n")


# 发送请求验证

title_list = []  # 标题
Content_Length_list = []  # 响应包长度


def process_data(lt, out_name, error_int, code_list, retry):
    # p_lt = []  # 最终结果列表
    # num = 0  # 测试url定位
    Response_error = error_int  # 响应包误差波动值

    for i in lt:

        try:

            r = requests_url(i)
            r.html.render(sleep=2)
            # p = r.html.html
            # print(p)
            content_length = len(r.content)
            print('')
            print(r.status_code)
            # print(content_length)
            content_type = r.headers.get('content-type')

            if r.status_code not in code_list:
                if r.status_code in skip_43:  # 若想多搜集403or404资产建议关闭响应包筛选and content_length not in Content_Length_list:
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


                    # print(r.encoding)
                    # r.encoding = 'gbk'
                    # content = r.text.replace('\r', '').replace('\n', '').replace(' ', '')
                    # output_data(content, 'title.txt')
                    # print(content)

                    # node = r.html.find('title', first=True)
                    whether_title = bool(r.html.find('title', first=True))

                    if whether_title:
                        node = r.html.find('title', first=True)
                        title_text = node.text
                        print(title_text)
                        skip_titles = skip_title
                        # print(skip_titles)
                        flag = bool(re.findall(skip_titles, title_text))
                        if flag:
                            continue
                        if title_text not in title_list or content_length not in Content_Length_list:
                            title_list.append(title_text)
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
                            output_data(i, 'repeat.txt')
                            continue
                    else:
                        # 写入检测是否需要执行js跳转，windows.location
                        print("{}  可成功访问".format(i))

                        output_data(i, '改url未检索到标题.txt')


            else:
                print("{}  不能成功访问,响应码为{}".format(i, r.status_code))
                print('')

                continue

        except:
            cs = retry  # 设置重连次数
            for c in range(cs):
                c += 1
                time.sleep(2)
                if c == cs:
                    print('')
                    print("{}   访问超时".format(i))
                    output_data(i, '访问超时.txt')
                    continue

    return title_list, Content_Length_list


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
    process_data(lt, out_name, error_int, code_list, retry)
    #
    # thread_list = []
    # thflist = [[] for i in range(numbers)]
    # for i, e in enumerate(lt):
    #     thflist[i % numbers].append(e)
    # for i in thflist:
    #     thread_list.append(i)
    # # print(thread_list)

    #
    # thread_list = [threading.Thread(target=process_data, args=(thread_list[i], out_name, error_int, code_list, retry))
    #                for i in range(len(thread_list))]
    # for thread in thread_list:
    #     thread.start()
    # for thread in thread_list:
    #     thread.join()

    print('')
    print("可成功访问的url已保存在{}文件中.".format(out_name))
    sys.exit()


if __name__ == "__main__":
    main()