import random
import requests
from threading import Thread
import time
import MySQLdb
from requests import ConnectTimeout, ReadTimeout
from typing import Optional
from requests.exceptions import ProxyError, ChunkedEncodingError
from queue import Queue
from variable import *


class CrawBaseException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class RequestException(CrawBaseException):
    def __init__(self, msg):
        super().__init__(msg)


class SqlAlreadyExistsException(CrawBaseException):
    def __init__(self, msg):
        super().__init__(msg)


class SqlInsertException(CrawBaseException):
    def __init__(self, msg):
        super().__init__(msg)


class UserNotFoundException(CrawBaseException):
    def __init__(self, msg):
        super().__init__(msg)


class ResManager:

    def __init__(self, max_size=4096) -> None:
        super().__init__()
        self._queue = Queue(max_size)

    def get_task(self):
        return self._queue.get()

    def put_task(self, url):
        self._queue.put(url)


res_manager = ResManager(max_size=4096)


class Worker(Thread):

    def __init__(self, name) -> None:
        super().__init__(name=name)
        self.headers = {
            'Host': 'api.bilibili.com',
            'Origin': PAGE_URL,
            'Referer': f'{PAGE_URL}/{random.randint(1, 100000)}',
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': 'application/json',
            'Connection': 'close',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.cur_proxy = {'https': f'https://{random.choice(PROXIES)}'}

    def run(self) -> None:
        print(f'爬虫线程:{self.name}开始执行...')
        conn = MySQLdb.connect(host=DB_HOST, user=DB_USER,
                               passwd=DB_PASSWORD, db=DB_NAME, port=DB_PORT, charset='utf8')
        cur = conn.cursor()
        while True:
            mid = res_manager.get_task()
            while True:
                self._update_req_info()
                try:
                    self._crawl(mid, cur)
                    break
                except RequestException:
                    # 如果是请求上的异常，则重试
                    # print(f'重新爬取用户:{mid}')
                    continue
                except SqlInsertException as e:
                    # 数据插入异常, 则插入异常记录
                    self._insert_failure_record(cur, mid, 0, e.msg)
                    break
                except UserNotFoundException as e:
                    self._insert_failure_record(cur, mid, 0, e.msg)
                    break
                except SqlAlreadyExistsException:
                    break
                except Exception as e:
                    continue
            conn.commit()
            time.sleep(random.uniform(FETCH_INTERVAL_MIN, FETCH_INTERVAL_MAX))

    def _crawl(self, mid, cur):
        """
        抓取并持久化用户信息
        :param mid: B站用户id
        :param cur: mysql游标
        :return: None
        """
        if self._is_member_exist(cur, mid):
            print(f'数据库中已存在此用户mid:{mid}, 忽略')
            return
        member_info = self._get_member_by_mid(mid)
        if member_info is None:
            return
        mid = int(member_info['mid'])
        name = member_info['name']
        sex = member_info['sex']
        rank = member_info['rank']
        fans = member_info['fans']
        friend = member_info['friend']
        level = member_info['level_info']['current_level']
        vip_type = member_info['vip']['vipType']
        try:
            cur.execute(f"INSERT INTO bilibili_member "
                        f"(mid, `name`,`sex`, `rank`,fans,friend, level, vip_type) "
                        f"VALUES "
                        f"({mid}, '{name}','{sex}', '{rank}', {fans}, {friend}, {level}, {vip_type})"
                        )
            print(f'成功插入用户数据: {mid}, 当前代理:{self.cur_proxy["https"]}')
        except MySQLdb.ProgrammingError as e:
            print(f'插入用户: {mid} 数据出错:{e}')
            raise SqlInsertException(str(e))
        except MySQLdb.IntegrityError:
            print(f'用户: {mid} 数据已存在,不作插入')
            raise SqlAlreadyExistsException('数据已存在')

    def _get_member_by_mid(self, mid: int) -> Optional[dict]:
        """
        根据用户id获取其信息
        :param mid: B站用户id
        :return: 用户详情 or None
        """
        get_params = {
            'mid': mid,
            'jsonp': 'jsonp'
        }
        try:
            res_json = requests.get(API_MEMBER_INFO, params=get_params, timeout=WAIT_MAX, proxies=self.cur_proxy,
                                    headers=self.headers).json()
        except ConnectTimeout as e:
            print(
                f'获取用户id: {mid} 详情失败: 请求接口超时, 当前代理:{self.cur_proxy["https"]}')
            raise RequestException(str(e))
        except ReadTimeout as e:
            print(
                f'获取用户id: {mid} 详情失败: 接口读取超时, 当前代理:{self.cur_proxy["https"]}')
            raise RequestException(str(e))
        except ValueError as e:
            # 解析json失败基本上就是ip被封了
            print(
                f'获取用户id: {mid} 详情失败: 解析json出错, 当前代理:{self.cur_proxy["https"]}')
            raise RequestException(str(e))
        except ProxyError as e:
            print(
                f'获取用户id: {mid} 详情失败: 连接代理失败, 当前代理:{self.cur_proxy["https"]}')
            raise RequestException(str(e))
        except requests.ConnectionError as e:
            # 可以断定就是代理IP地址无效
            print(f'获取用户id: {mid} 详情失败: 连接错误, 当前代理:{self.cur_proxy["https"]}')
            raise RequestException(str(e))
        except ChunkedEncodingError as e:
            print(
                f'获取用户id: {mid} 详情失败: 远程主机强迫关闭了一个现有的连接, 当前代理:{self.cur_proxy["https"]}')
            raise RequestException(str(e))
        else:
            if res_json['code'] == -404:
                print(f'找不到用户mid:{mid}')
                raise UserNotFoundException(f'找不到用户mid:{mid}')
            if 'data' in res_json:
                if res_json['data']['card']['fans'] < 5000 or res_json['data']['card']['fans'] > 50000:
                    print(f'用户不符合要求mid:{mid}')
                    raise UserNotFoundException(f'用户不符合要求mid:{mid}')
                else:
                    return res_json['data']['card']
            print(f'获取用户id: {mid} 详情失败: data字段不存在!')
        return

    def _update_req_info(self):
        """
        更新请求信息, 主要用于防反爬
        :return:
        """
        self.headers.update({
            'Referer': f'{PAGE_URL}/{random.randint(1, 100000)}',
            'User-Agent': random.choice(USER_AGENTS),
        })
        self.cur_proxy.update({
            'https': f'https://{random.choice(PROXIES)}',
            'http': f'http://{random.choice(PROXIES)}',
        })

    @staticmethod
    def _insert_failure_record(cur, mid, state, remark):
        remark = remark.replace("'", "\\\'")
        try:
            cur.execute(
                "INSERT INTO failure_record (mid, remark, state) "
                f"VALUES ({mid}, '{remark}', '{state}')"
            )
        except MySQLdb.ProgrammingError as e:
            print(f'插入失败日志: {mid} 数据出错:{e}')
        except MySQLdb.IntegrityError:
            print(f'失败日志: {mid} 数据已存在,不作插入')

    @staticmethod
    def _is_member_exist(cur, mid):
        cur.execute(
            "SELECT COUNT(*) FROM bilibili_member "
            f"WHERE mid={mid}"
        )
        return cur.fetchone()[0] == 1


class Distributor(Thread):
    """
    任务分发线程,负责下发任务(用户mid)到队列
    """

    def __init__(self, start: int, end: int):
        super().__init__()
        self._start = start
        self._end = end

    def run(self) -> None:
        print('Distributor开始执行...')
        for mid in range(self._start, self._end):
            res_manager.put_task(mid)
        print('Distributor执行完毕')


class BilibiliMemberCrawler:
    """
    B站爬虫入口,用于初始化配置与开启线程
    """
    @classmethod
    def start(cls):
        cls.init()
        # 开启任务分发线程
        Distributor(FETCH_MID_FROM, FETCH_MID_TO + 1).start()
        # 开启爬虫线程
        for i in range(0, THREADS_NUM):
            Worker(f'Worker-{i}').start()

    @staticmethod
    def init():
        """
        读取并初始化浏览器agent
        """
        with open('user-agents.txt', 'rb') as uaf:
            for ua in uaf.readlines():
                if ua:
                    USER_AGENTS.append(ua.strip()[:-1])
        random.shuffle(USER_AGENTS)
        # 初始化本地代理池
        if USE_PROXY_POOL:
            try:
                res = requests.get(PROXY_POOL_URL)
                if res.status_code == 200:
                    data = res.json()['data']
                    for ip in data:
                        ip_add=ip['ip']+':'+str(ip['port'])
                        PROXIES.append(ip_add)
                print(f'初始化本地代理池成功，共{len(PROXIES)}个')
            except Exception as e:
                print(f'初始化本地代理池失败！！{e}')

if __name__ == '__main__':
    BilibiliMemberCrawler.start()
