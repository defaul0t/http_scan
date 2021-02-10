# http_scan

#### 一款低效的URL资产探测工具，用于验证大量URL状态，常用于SRC资产筛选，觉得低效的表哥可以点个** <br>



python3 http_scan.py -u url.txt -c 404 403 -t 5 -r 1 -e 2 -o output.txt <br>


![http_scan](https://github.com/daichao66/http_scan/blob/main/http_scan.png)


#### 更新日志(2020/11/10)

多线程验证功能，输出功能优化

#### 更新日志(2020/11/12)

修复标题验证bug，加入了某些url请求后执行js跳转的验证

#### 更新日志(2021/2/9)
上传了微改的request书写的py脚本，已经间接解决了大部分问题，可以正常使用脚本过滤资产：<br>
1.对所有资产进行分类<br>
2.通过正则过滤类似标题网站，如：北京taobao，天津信息分类门户等等这种有大量地名但是框架类似的网站<br>
3.由js跳转的url将不再丢弃，存入未获取标题文本中<br>
<br>
上传了request_html书写的py脚本，已经间接解决了大部分问题，可以正常使用脚本过滤资产：<br>
1.该库有模拟浏览器访问的render函数功能，解决了javascript带来的资产误识别<br>
2.缺陷：未解决多线程冲突，似乎和render函数有关系，采用多进程容易崩溃，有大佬会的，联系我，学习交流下，微信：REMxMzIwMjIyMTQ3<br>
