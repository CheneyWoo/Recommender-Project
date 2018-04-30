#!/usr/bin/python
# -*- coding:UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import requests
from bs4 import BeautifulSoup as bs
from collections import OrderedDict

urlLists = ['http://detail.zol.com.cn/series/16/160/param_20667_0_1.html',
           'http://detail.zol.com.cn/series/16/160/param_20435_0_1.html',
           'http://detail.zol.com.cn/series/16/160/param_22104_0_1.html',
           'http://detail.zol.com.cn/series/16/160/param_20085_0_1.html',
           'http://detail.zol.com.cn/series/16/160/param_20191_0_1.html'
           ]
for urlList in urlLists:
    source = requests.get(urlList);
    soup = bs(source.text, 'lxml');
    product_table = OrderedDict();

    table = soup.find('table', id='seriesParamTable');
    rows = table('tr');
    # print rows;
    # prices = soup.find_all('b', class_ = "");
    # prices = prices[2:]
    series = soup.find('h1',class_ = "ptitle");
    print series; #用于检验是否成功解析tag
    prices = table('b');
    print prices; #用于检验是否成功解析tag

    for row in rows:
        if str(row.th.string) == '包装清单' or str(row.th.string) == '详细内容' \
                or str(row.th.string) == '价格/商家' or str(row.th.string) == '图片':
            continue;
        else:
            product_table[str(row.th.string)] = list(row.stripped_strings)[1:];
    product_table['价格/商家'] = prices;

    with open('/Users/CheneyWu/Desktop/Learning Stuff/Scientific Research/result2.csv', 'a') as file:
        file.write(series.string+'\n');
        for th in product_table.keys():
            file.write(th + ',');
            templist = list(product_table[th]);
            rawstring = str(templist)[1:][:-1];
            processed_string = rawstring + '\n';
            processed_string = processed_string.decode('unicode-escape');
            processed_string = processed_string.replace('u', ' ').replace("'", ' ');
            processed_string = processed_string.replace("<b class=\"\">", ' ').replace("</b>", ' ')
            # print processed_string;
            processed_string = processed_string.encode('utf-8');
            # print isinstance(processed_string, unicode);
            # print processed_string.__class__;
            file.write(processed_string);
        file.write('\n');