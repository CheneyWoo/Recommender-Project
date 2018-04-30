from collections import OrderedDict
from bs4 import BeautifulSoup as BS
import requests

param_dict = OrderedDict()

def write_first_row():
    with open("all_param.txt", 'r') as f_param:
        for param in f_param.readlines():
            param_dict[param.strip()] = None
            # 把文件中的所有参数按照顺序加载到有序字典里
    with open("result.csv", 'w+') as f_result:
        for key in param_dict.keys():
            f_result.write(key + ',')
        f_result.write('\n')
        # 第一行打印完毕

def get_page(url):  # page是已经煲成汤的网页
    #防止反爬虫机制
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    global page
    page = requests.get(url, headers=headers)
    page=BS(page.text, 'lxml')

def product_num():  # 获取该page表示的系列包含多少产品
    css_path = 'body > div.wrapper.clearfix > div.module > div.mod_bd.mod_series_param > dl > dd > span > b'
    num = int(str(page.select(css_path))[4:][:-5])
    return num

def download_one_series():  #爬取一个page中所有参数对应的值存入param_dict字典中
    num_of_product = product_num()
    table_in_page = page.find(id='seriesParamTableBox')
    with open("result.csv", 'a+') as f_result:
        for i in range(num_of_product): #遍历
            # e.table.find_all('tr', recursive=False): #遍历每一个产品的每一个参数
                if len(row('td')) != 0:  #必须是有内容的一行
                    if not (row.th.string in param_dict):#字典里不存在的属性值不加入
                        continue
                    if row.th.string == '价格/商家':
                        # 存入字典，字典中每一个键对应一个值的数组
                        param_dict[row.th.string] = (row('td')[i].select('div > span.price > b')[0].string)
                    else:
                        param_dict[row.th.string] = row('td')[i].string
            if row.th.string == '型号':
                print(row('td')[i].string)
            for value in param_dict.values(): #不存在参数对应值则设置为NULL
                if value == None:
                    value = 'NULL'
                try:
                    f_result.write(value.strip().replace(',','，') + ',') #每一个产品写一行
                except:
                    print('有错误')
                    f_result.write(',')
            f_result.write('\n')  #每个产品对应参数写一行后换行
        print("该系列（含%d个单品）处理完毕" % num_of_product)
    return num_of_product

class Page():
    def __init__(self, url):  # 构造函数实际上规定了哪些参数必须传进来当做实例变量 self就代表一个实例
        self.url = url
        get_page(self.url)
        # 构造函数在创建实例的时候自动执行。因此这句话的任务是，每次构建实例时传入一个url，全局变量（只需在创建时声明一次）page都自动更新
        self.num_of_product=download_one_series()
