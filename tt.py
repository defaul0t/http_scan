import pop as pop
import requests
import bs4
import lxml
import threading
import re
from multiprocessing.dummy import Pool
requests.packages.urllib3.disable_warnings()
code_list = [500, 501, 502, 503, 504, 505, 401, 402, 400]
skip_43 = [404, 403]
skip_list = []
title_list= []
headersone = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
def demo(ip_hosts):

    for a in range(len(ip_hosts)):

        headers = {'Host': ip_hosts[a][1],
                   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}

        try:
            onetext = requests.get(ip_hosts[a][0], headers=headersone, verify=False, timeout=3).text
            onecode = requests.get(ip_hosts[a][0], headers=headersone, verify=False, timeout=3).status_code
            # onetext = geturl(ip_hosts[a][0])[0]
            # onecode = geturl(ip_hosts[a][0])[1]

            res = requests.get(ip_hosts[a][0], headers=headers, verify=False, timeout=2)
            # t = bs4.BeautifulSoup(res.text, 'lxml').find("title").string

            twotext = len(res.text)
            twocode = res.status_code

            res.encoding = res.apparent_encoding
            content = res.text.replace('\r', '').replace('\n', '').replace(' ', '')
            whether_title = bool(re.findall(r"(?<=><title>)(.+?)(?=</title>)", content))
            title = re.findall('(?<=><title>)(.+?)(?=</title>)', content)[0]
            print("{}  探测中...".format(ip_hosts[a][1]))
            if onetext != twotext or onecode != twocode:
                if ip_hosts[a][1] in skip_list or title in title_list or bool(re.findall("Cloudflare", title))==True:
                    continue

                elif twocode in code_list:
                    continue

                elif twocode in skip_43:
                    output_data(str(u), '40x.txt')
                    skip_list.append(str(ip_hosts[a][1]))

                    continue

                elif whether_title:
                    print('可能存在host碰撞')
                    title_list.append(title)
                    u = ip_hosts[a][0] + '   ' + ip_hosts[a][1] + '   ' + str(len(res.text)) + '   ' + title
                    # print(title)
                    print(u)
                    output_data(str(u), '可能存在host碰撞.txt')
                    skip_list.append(str(ip_hosts[a][1]))
                    continue

                elif whether_title == False:
                    print('no title')
                    output_data(str(u), 'notitle.txt')
                    skip_list.append(str(ip_hosts[a][1]))
                else:
                    continue

                continue
            else:

                print('未检测到变化，已跳过')
                continue

        except:
            pass


    return skip_list




def output_data(i, out_name):
    with open(out_name, "a") as f:
        f.write(i + "\n")
# def geturl(url):
#     try:
#         headers = {
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36'}
#         r = requests.get(url, headers=headers, verify=False)
#         onetext = len(r.text)
#         onecode = r.status_code
#         return onetext, onecode
#     except:
#         pass


def make_payload(ips,hosts):
    payload=[]
    for ip in ips:
        for host in hosts:
            payload.append(("https://"+ip,host))
            payload.append(("http://"+ip,host))
    return payload

def make_payload_c(ips_c,hosts):
    payload=[]
    u = []
    for i in range(256):
        for ip in ips_c:
            u.append(ip+"."+str(i))
    for ip in u:
        for host in hosts:
            payload.append(("https://"+ip,host))
            payload.append(("http://"+ip,host))
    return payload

def readlist():
    with open('ip.txt', "r")as f:
        s = f.readlines()
        ips = [i.strip() for i in s]
        with open('host.txt', "r")as f:
            s = f.readlines()
            hosts = [i.strip() for i in s]

        return ips,hosts



# ips=["1.1.1.1","2.2.2.2"] 
# d=make_payload(ips,hosts) #可以先用ip跑一下，没有收获选择跑C段

# ipc = ["1.1.1"]
# hosts=["a.huoxian.cn"]



def main():
    ips = readlist()[0]
    hosts = readlist()[1]
    d = make_payload(ips, hosts)

    print(len(d))
    thread_list = []
    thflist = [[] for i in range(50)]
    for i, e in enumerate(d):
        thflist[i % 50].append(e)
    for i in thflist:
        thread_list.append(i)
    # print(thread_list)

    thread_list = [threading.Thread(target=demo, args=(thread_list[i],))
                   for i in range(len(thread_list))]
    for thread in thread_list:
        thread.start()
    for thread in thread_list:
        thread.join()


if __name__ == "__main__":
    main()