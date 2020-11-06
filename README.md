# http_scan

这个是一款低效的URL资产探测工具

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     target url file
  -c CODE [CODE ...], --code CODE [CODE ...]    自定义过滤状态码
                        skip status code
  -e ERROR, --error ERROR                       设置过滤的响应包波动值
                        response packet error
  -r RETRY, --retry RETRY                       设置等待重连的次数
                        Timeout reconnection
  -t THREADS, --Threads THREADS                 设置线程数
                        number of threads,default = 5
  -o OUTPUT, --output OUTPUT                     自定义输出文本名
                        result
