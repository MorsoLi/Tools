# 用户信息页面URL
PAGE_URL = 'http://space.bilibili.com'
# 获取用户信息接口
API_MEMBER_INFO = 'https://api.bilibili.com/x/web-interface/card'

# MySQL配置
DB_HOST = 'localhost'
DB_PORT = 3306
DB_USER = 'root'
DB_PASSWORD = '123456'
DB_NAME = 'bilibili'

USE_PROXY_POOL = True
# 芝麻付费代理API 获取链接
PROXY_POOL_URL = 'http://webapi.http.zhimacangku.com/getip?num=20&type=2&pro=&city=0&yys=0&port=1&pack=77438&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions='
# 代理设置(需要自行添加), 如果
PROXIES=['101.37.118.54:8888','36.25.243.251:80','36.189.224.204:80','162.243.108.129:8080']
# 浏览器agent列表, 初始化时会加附加上user-agents.txt里的内容
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:67.0) Gecko/20100101 Firefox/67.0'
]
# 抓取等待最大时间(s)
WAIT_MAX = 2
# 开启抓取线程的数量
THREADS_NUM = 1
# 每条线程抓取的间隔范围(s)
FETCH_INTERVAL_MIN = 0.01
FETCH_INTERVAL_MAX = 0.05
# 想要抓取的用户id范围
FETCH_MID_FROM = 1
FETCH_MID_TO = 3