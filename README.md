# http_scan

#### 一款低效的URL资产探测工具，用于验证大量URL状态，常用于SRC资产筛选，觉得低效的表哥可以点个** <br>



python3 http_scan.py -u url.txt -c 404 403 -t 5 -r 1 -e 2 -o output.txt <br>


![http_scan](https://github.com/daichao66/http_scan/blob/main/http_scan.png)


#### 更新日志(2020/11/10)

多线程验证功能，输出功能优化

#### 更新日志(2020/11/12)

修复标题验证bug，加入了某些url请求后执行js跳转的验证
