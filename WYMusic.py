import requests
import time
from contextlib import closing
import sys
class ProgressBar(object):

    def __init__(self, title,
                 count=0.0,
                 run_status=None,
                 fin_status=None,
                 total=100.0,
                 unit='', sep='/',
                 chunk_size=1.0):
        super(ProgressBar, self).__init__()
        self.info = "【%s】%s %.2f %s %s %.2f %s"
        self.title = title
        self.total = total
        self.count = count
        self.chunk_size = chunk_size
        self.status = run_status or ""
        self.fin_status = fin_status or " " * len(self.status)
        self.unit = unit
        self.seq = sep

    def __get_info(self):
        # 【名称】状态 进度 单位 分割线 总数 单位
        _info = self.info % (self.title, self.status,
                             self.count/self.chunk_size, self.unit, self.seq, self.total/self.chunk_size, self.unit)
        return _info

    def refresh(self, count=1, status=None):
        self.count += count
        # if status is not None:
        self.status = status or self.status
        end_str = "\r"
        if self.count >= self.total:
            end_str = '\n'
            self.status = status or self.fin_status
        print(self.__get_info(), end=end_str)
class MusicDownload(object):
    def __init__(self,song=None):
        self.song=song
        self.url="https://api.imjad.cn/cloudmusic/?type=search&search_type=1&s="+str(self.song)
        self.header={
            'User-Agent':('Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D)' 
            'AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166  Safari/535.19')
        }
    def getMessage(self):
        song_message=[]
        response=requests.get(url=self.url,headers=self.header).json()
        for key in response.keys():
            if key=="result":
                for key1 in response[key].keys():
                    if key1=="songs": 
                        messList=response[key][key1]
        for i in range(len(messList)):    
            d={}
            for key,value in messList[i].items():
                if key=="name" or key=="id":
                    d[key]=messList[i][key]
                if key=="ar":
                    for key1 in messList[i][key][0].keys():
                        if key1=="name":
                            d["歌手"]=messList[i][key][0][key1]
                if key=="al":
                    for key2 in messList[i][key].keys():
                        if key2=="name":
                            d["来源"]=messList[i][key][key2]
                        if key2=="picUrl":
                            d["图片"]=messList[i][key][key2]    
            song_message.append(d)
        return song_message
    def getSong(self):
        song_message=self.getMessage()
        url2="https://api.imjad.cn/cloudmusic/?type=song&id="+str(song_message[0]["id"])
        response=requests.get(url2,headers=self.header)
        response=response.json()
        for key in response.keys():
            if key=="data":
                newurl=response[key][0]["url"]
        with closing(requests.get(newurl,stream=True)) as response2:
            chunk_size=1024
            content_size=int(response2.headers["content-length"])
            print(content_size)
            file_name="/home/mygodot/音乐/"+ "/"+ '%s.mp3'%self.song
            progress = ProgressBar(file_name, total=content_size,
                                     unit="KB", chunk_size=chunk_size, run_status="正在下载", fin_status="下载完成")
            with open(file_name, "wb") as file:
                for data in response2.iter_content(chunk_size=chunk_size):
                    file.write(data)
                    progress.refresh(count=len(data))
                    
        '''
        path="/home/mygodot/音乐/"
        with open(path + "/"+ '%s.mp3'%self.song,'wb') as f:
            response2=requests.get(newurl,headers=self.header)
            f.write(response2.content)
            time.sleep(1)    
        '''  
if __name__=="__main__":
    song=sys.argv[1]
    ex=MusicDownload(song)
    ex.getSong()

