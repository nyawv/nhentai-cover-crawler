import requests
import queue
import re
import os
import time
import threading
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)  # 关闭无证书安全警告

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/92.0.4515.159 Safari/537.36',
}

proxies = {
    'https': 'http://127.0.0.1:1008',
    'http': 'http://127.0.0.1:1008'
}

s = requests.session()
s.headers.update(headers)
s.proxies.update(proxies)  # 不挂代理删除这一行
s.verify = False
p_q = queue.Queue()
q = queue.Queue()


def get_page_url():
    for page in range(st_page, end_page + 1):
        page_url = url + "&page=" + str(page)
        p_q.put({"page_url": page_url, "page": page})


def get_img_url():
    while not p_q.empty():
        data = p_q.get()
        r = s.get(data["page_url"])
        soup = BeautifulSoup(r.content.decode('utf-8'), 'lxml')
        s_0 = soup.find('div', class_="container index-container")
        s_1 = s_0.find_all("div", class_="gallery")
        for i in s_1:
            s_img = i.find("img", class_="lazyload")
            s_url = s_img["data-src"].replace("thumb", "1").replace("t.", "i.")  # 直接将获取的预览图片网址改为其第一页图片网址
            s_name = i.find('div', class_="caption").string
            q.put({"s_url": s_url, "s_name": s_name, "num": i, "page": data["page"]})
            time.sleep(0.4)


def get_img(t):
    while not q.empty():
        try:
            img = q.get()
            img_get = s.get(img["s_url"])
            olds = r"[\/\\\:\*\?\"\<\>\|\']"
            new_name = re.sub(olds, " ", repr(img["s_name"]))  # 消除文件名不能带有的符号和转义符
            out_path = ".\\" + "nhcover" + "\\"  # 存储文件夹路径
            out_name = out_path + str(new_name) + ".png"
            if not os.path.exists(out_path):
                os.mkdir(out_path)  # 如果不存在该文件夹则创建
            with open(out_name, 'wb') as f:
                f.write(img_get.content)
                f.close()
            print("线程" + str(t) + "：图像(页数：" + str(img["page"]) + ")" + str(new_name) + "已储存")
        except requests.exceptions.ProxyError:
            print("：图像(页数：" + str(q.get()["page"]) + ")" + str(q.get()["s_name"]) + "获取失败")
            time.sleep(4)


def start_get():
    get_page_url()
    print("正在获取封面图片网址，请稍等")
    for t in range(thread_num):
        t = threading.Thread(target=get_img_url)
        t.start()
        t.join()

    for t in range(thread_num):
        t = threading.Thread(target=get_img, args=(t,))
        t.start()


if __name__ == '__main__':
    url = "https://nhentai.net/search/?q=Language%3A%E2%80%9Dchinese%E2%80%9C+%2B+tags%3A%22lolicon%22+-tags%3A%22big" \
          "+breasts%22&sort=popular"  # 填入需要爬取页面的网址，如上（不带页码）
    st_page = 1  # 爬取的初始页码
    end_page = 400  # 爬取的结束页码
    thread_num = 4  # 线程数
    start_get()
