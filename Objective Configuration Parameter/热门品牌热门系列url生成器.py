#生成热门品牌热门系列的URL,并存入一个文本文件
import requests
from bs4 import BeautifulSoup as BS
from collections import OrderedDict

front_page=requests.get('http://detail.zol.com.cn/notebook_index/subcate16_list_1.html')#下载网页
front_page=BS(front_page.text,'lxml')#将网页交给BS库
brand_list=front_page.find(id='J_ParamBrand')#定位产品名列表
brand_url=OrderedDict()
def process_series_url(raw_url):
    raw_url = raw_url.replace("/s", "http://detail.zol.com.cn/s")
    raw_url = raw_url.replace("16/", "16/160/param_")
    raw_url = raw_url.replace("_1.html", "_0_1.html")
    return raw_url
with open('D:\hot series.txt','w+') as f:
    for href in brand_list.find_all('a'):
        if href.string=='中柏':
            break
        brand_url[href.string]='http://detail.zol.com.cn'+href['href']
    for brand,url in brand_url.items():
        f.write(brand+' 的热门系列参数网址：\n')
        series_page=requests.get(url)#下载网页
        series_page=BS(series_page.text,'lxml')#将网页交给BS库
        series_list=series_page.find(id='J_SeriesFilter')#定位系列列表
        for series in series_list.div.find_all('a',recursive=False):
            f.write(process_series_url(series['href'])+'\n')
