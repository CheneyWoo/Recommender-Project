import requests
from bs4 import BeautifulSoup as BS

with open(r"hot_series.txt",'r') as f:
    series_list=[];
    for line in f.readlines():
        if line.startswith('h'):
            series_list.append(line.strip()); #移除字符串首尾的空格

series_set=set(); #创建一个无序不重复元素集
count = 0;
for series in series_list:
    page=BS(requests.get(series).text,'lxml');
    table_in_page=page.find(id='seriesParamTableBox').table;
    for row in table_in_page.find_all('tr',recursive=False):
        series_set.add(row.th.string);
    count += 1;
    print("检索了第%d个系列"%count);
with open(r"all_param.txt",'w+') as f:
    for param in series_set:
        f.write(param+'\n');
