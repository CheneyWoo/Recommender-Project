#!/usr/bin/python
# -*- coding:UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
from bs4 import BeautifulSoup as BS
from collections import OrderedDict

source=requests.get('http://detail.zol.com.cn/series/16/21/param_18548_0_1.html')
soup=BS(source.text,'lxml')
product_table=OrderedDict()
#total_products=soup.find(name='span',class_="total").b.string#这个变量保存总的产品数
#print(total_products)

table=soup.find('table',id='seriesParamTable')
rows=table('tr')

for row in rows:
    product_table[str(row.th.string)]=list(row.stripped_strings)[1:]

with open('/Users/CheneyWu/Desktop/Learning Stuff/Scientific Research/result2.txt','w') as f:
    for th in product_table.keys():
        if th=='包装清单':continue
        f.write(th+',')
        templist = list(product_table[th])
        if th == '详细内容':
            print(len(templist))
            for i in range(len(templist)):
                try:
                    templist.remove("进入官网>>")
                except BaseException:
                    break
        rawstring = str(templist)[1:][:-1] #原始字符串
        processed_string = rawstring.replace(',',' ').replace(', ',',')+'\n'
        f.write(processed_string)
        #f.write(rawstring)
        #f.write(str(templist))


