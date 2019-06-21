# -*- coding:utf-8 -*-
from django.http import HttpResponse
import pandas as pd
import numpy as np
import math
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
import json
import memcache
from bs4 import BeautifulSoup as BS
import requests
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import jieba
import jieba.posseg as pseg
import base64
import datetime


#导入数据
dataframe = pd.read_excel(r"product.xlsx")
information = np.array(dataframe)
product = dataframe.iloc[:,5:17]
product = np.array(product)

index_3000 = []
index_5000 = []
index_8000 = []
index_10000 = []
index_13000 = []
index_17000 = []
index_20000 = []

def SelectByPrice(price,cluster):
    return {
        '3000': np.concatenate([product[cluster == num, :] for num in index_3000]),
        '5000': np.concatenate([product[cluster == num, :] for num in index_5000]),
        '8000': np.concatenate([product[cluster == num, :] for num in index_8000]),
        '10000': np.concatenate([product[cluster == num, :] for num in index_10000]),
        '13000': np.concatenate([product[cluster == num, :] for num in index_13000]),
        '17000': np.concatenate([product[cluster == num, :] for num in index_17000]),
        '20000': np.concatenate([product[cluster == num, :] for num in index_20000]),
    }.get(price, 'error')

def ClusterByPrice(product, price):
    n_clusters = 15
    kmeans = KMeans(n_clusters)
    kmeans.fit(product)
    np.set_printoptions(suppress=True)
    #print(kmeans.cluster_centers_)
    cluster = kmeans.fit_predict(product)
    price_means = []
    for i in range(n_clusters):
        price_mean = [item[0] for item in product[cluster == i, :]]
        price_means.append(np.mean(price_mean))
        #print np.mean(price_mean), i
    sort_price = np.sort(price_means)

    for item in sort_price:
        num = price_means.index(item)
        if 2000 <= item < 4000:
            index_3000.append(num)
        elif 4000 <= item < 6000:
            index_5000.append(num)
        elif 6000 <= item < 9000:
            index_8000.append(num)
        elif 9000 <= item < 12000:
            index_10000.append(num)
        elif 12000 <= item < 15000:
            index_13000.append(num)
        elif 15000 <= item < 20000:
            index_17000.append(num)
        elif 20000 <= item:
            index_20000.append(num)

    candidate_sample = SelectByPrice(price, cluster)
    return candidate_sample

def SelectByWeight(weight_list, candidate_samples):
    #选择最合适的产品
    #weight_list = [1,1,1,9,9,1,1,1,1]
    similarity = []
    for candidate_sample in candidate_samples:
        calculate = np.array([weight_list,candidate_sample[1:]])
        similarity.append(cosine_similarity(calculate)[0][1])
    similarity = list(set(similarity))
    candidate_index = np.sort(similarity)[-100:]
    candidates = []
    for item in candidate_index:
        candidate = candidate_samples[similarity.index(item)]
        candidates.append(candidate)
    product_index = []
    for candidate in candidates:
        product_index.append(product.tolist().index(candidate.tolist()))
    return product_index

#ID3部分
#筛选数据
attributes = ['color', 'touchscreen', 'deformation', 'fingerprint']
def Data(product_index):
    data = np.array(dataframe.iloc[:,17:])
    dataSet = [data[x] for x in product_index]
    return dataSet

#计算熵值
def calcEnt(dataSet,i):
    labels = set([dataVec[i] for dataVec in dataSet])
    labelSet = {}
    for label in labels:
        labelSet[label] = 0
    #样本总个数
    totalNum = len(dataSet)
    #类别集合
    #计算每个类别的样本个数
    for dataVec in dataSet:
        label = dataVec[i]
        if label not in labelSet.keys():
            labelSet[label] = 0
        labelSet[label] += 1
    Ent = 0
    #计算熵值
    for key in labelSet:
        pi = float(labelSet[key])/totalNum
        Ent -= pi*math.log(pi,2)
    return Ent

#按给定特征划分数据集:返回第featNum个特征其值为value的样本集合，且返回的样本数据中已经去除该特征
def splitDataSet(dataSet, featNum, featvalue):
    retDataSet = []
    for dataVec in dataSet:
        if dataVec[featNum] == featvalue:
            splitData = dataVec[:featNum]
            splitData = np.append(splitData,dataVec[featNum+1:])
            retDataSet.append(splitData)
    return np.array(retDataSet)

#选择最好的特征划分数据集
def chooseBestFeatToSplit(dataSet, labelSet):
    featNum = len(labelSet)
    maxEnt = 0
    bestFeat = -1
    #以每一个特征进行分类，找出信息熵最大的特征
    for i in range(featNum):
        Ent = calcEnt(dataSet,i)
        #print labelSet[i],Ent
        if Ent >= maxEnt:
            maxEnt = Ent
            bestFeat = i
    return bestFeat

def createDecisionTree(dataSet, featName):
    #数据集的分类类别
    sample_collection = [dataVec[-1] for dataVec in dataSet]
    #所有特征已经遍历完，停止划分，返回集合中的样本
    if len(dataSet[0]) == 1:
        return sample_collection
    if len(sample_collection) == sample_collection.count(sample_collection[0]):
        return sample_collection
    #选择最好的特征进行划分
    bestFeat = chooseBestFeatToSplit(dataSet, featName)
    bestFeatName = featName[bestFeat]
    #print "当前最佳属性是", bestFeatName
    featName = featName[:bestFeat]+featName[bestFeat+1:]
    #del featName[bestFeat]
    #以字典形式表示树
    DTree = {bestFeatName:{}}
    #根据选择的特征，遍历该特征的所有属性值，在每个划分子集上递归调用createDecisionTree
    featValue = [dataVec[bestFeat] for dataVec in dataSet]
    featValue = set(featValue)
    #print "剩余候选属性是", featName
    for value in featValue:
        subFeatName = featName[:]
        DTree[bestFeatName][value] = createDecisionTree(splitDataSet(dataSet,bestFeat,value), subFeatName)
    return DTree

def getWordCloud(productUrl):
    def getCommentIndex(producturl):
        indexNum = productUrl.split('/')[-1].split('.')[0][5:]
        url1 = "http://detail.zol.com.cn/xhr4_Review_GetList_%5EproId={}%5Epage=1.html".format(indexNum)
        return indexNum, url1
    index, url1= getCommentIndex(productUrl)
    text = ""
    cloud = WordCloud(
        # 设置字体，不指定就会出现乱码
        font_path=r"Deng.ttf",
        width=1024,
        height=768,
        background_color='white',
        max_words=50,
        max_font_size=200
    )
    def get_page_num(url1):
        r = requests.get(url1)
        data = json.loads(r.text)
        items = int(data['total'])
        return items // 10 + 1
    def getArticleContent(ArticleUrl):
        print(ArticleUrl)
        ArticleContent = ""
        r = requests.get(ArticleUrl)
        soup = BS(r.text, 'lxml')
        paras = soup.find(class_='article-content').find_all("p")
        for para in paras:
            if para.string:
                ArticleContent += para.string
        return ArticleContent
    page_num = get_page_num(url1)
    for i in range(1, page_num):
        # 一页
        url = "http://detail.zol.com.cn/xhr4_Review_GetList_%5EproId={}%5Epage={}.html".format(index,i)
        r = requests.get(url)
        data = json.loads(r.text)
        soup = BS(data['list'], 'lxml')
        comments_items = soup.select(".comments-item")  # 所有的块
        for comments_item in comments_items:  # 一个块
            tag = comments_item.find(class_="view-more")
            if tag and tag.a['href'].startswith("http"):
                text += getArticleContent(tag.a['href'])
                # print(tag.a['href'])
                comments_item.decompose()  # 提取出网址之后这个comments_item就扔掉了
        wordss = soup.select(".words")
        for words in wordss:
            text += words.p.string
        words_articles = soup.select(".words-article")
        for words_article in words_articles:
            text += words_article.p.string
    print(len(text))
    if len(text) > 0:
        words_list = []
        temp_words_list = pseg.cut(text)
        for word, flag in temp_words_list:
            # print(word,flag)
            if flag != 'p' and flag != 'd' and flag != 'c' and flag != 'u' and flag != 'r' and flag != 'm':
                words_list.append(word)
        remove_words = {'电脑', '一点'}
        words_list = [item for item in words_list if item not in remove_words]
        cut_text = ' '.join(words_list)
        wCloud = cloud.generate(cut_text)
        plt.imshow(wCloud, interpolation='bilinear')
        plt.axis('off')
        plt.show()
        wCloud.to_file("CloudImage/" + index + ".png")
        with open("CloudImage/" + index + ".png", "rb") as f:
            base64_data = base64.b64encode(f.read())
            print base64_data
    else:
        base64_data = 0
        print "No words!"
    return len(text), base64_data

def Select(request, tree):
    if request.method == 'POST':
        # tree = cache.get('tree')
        attribute = tree.keys()[0]
        choice = tree[attribute].keys()
        print "当前属性", attribute
        print "可供选项", choice
        data = json.loads(request.body.decode())
        flag = data.has_key(attribute)
        if not flag:
            response = {}
            #print attribute
            if attribute == 'color':
                temp = {}
                temp['issuer'] = "robot"
                temp['type'] = "muti_picker"
                temp['time'] = datetime.datetime.now().isoformat() + 'Z'
                temp['data'] = {}
                temp['data']['tip'] = "您喜欢什么颜色的笔记本电脑（主色调）？"
                temp['data']['options'] = []
                color_list = choice
                color_dict = {'black': '黑色', 'blue': '蓝色', 'slivery': '银色', 'golden': '金色', 'pink': '粉色', 'white': '白色',
                              'red': '红色', 'gray': '灰色'}
                for color in color_list:
                    option = {}
                    option['label'] = color_dict[color]
                    option['value'] = color
                    option['selected'] = False
                    temp['data']['options'].append(option)
                temp['data']['response'] = "我选择的是%label选项"
            if attribute == 'fingerprint':
                temp = {}
                temp['issuer'] = "robot"
                temp['type'] = "muti_picker"
                temp['time'] = datetime.datetime.now().isoformat() + 'Z'
                temp['data'] = {}
                temp['data']['tip'] = "您对指纹识别功能是否有要求？"
                temp['data']['options'] = []
                choice_list = choice
                choice_dict = {0: '不想要指纹识别', 1: '想要指纹识别'}
                for choice in choice_list:
                    option = {}
                    option['label'] = choice_dict[choice]
                    option['value'] = choice
                    option['selected'] = False
                    temp['data']['options'].append(option)
                temp['data']['response'] = "我选择的是%label选项"
            if attribute == 'deformation':
                temp = {}
                temp['issuer'] = "robot"
                temp['type'] = "muti_picker"
                temp['time'] = datetime.datetime.now().isoformat() + 'Z'
                temp['data'] = {}
                temp['data']['tip'] = "您对笔记本电脑变形模式有要求吗？"
                temp['data']['options'] = []
                choice_list = choice
                choice_dict = {0: '既然不要翻转也不要插拔', 1: '想要翻转笔记本', 2: '想要插拔笔记本', 3: '想要翻转且能插拔的笔记本'}
                for choice in choice_list:
                    option = {}
                    option['label'] = choice_dict[choice]
                    option['value'] = choice
                    option['selected'] = False
                    temp['data']['options'].append(option)
                temp['data']['response'] = "我选择的是%label选项"
            if attribute == 'touchscreen':
                temp = {}
                temp['issuer'] = "robot"
                temp['type'] = "muti_picker"
                temp['time'] = datetime.datetime.now().isoformat() + 'Z'
                temp['data'] = {}
                temp['data']['tip'] = "您对屏幕触控有要求吗？"
                temp['data']['options'] = []
                choice_list = choice
                choice_dict = {0: '不要触控屏', 1: '想要触控屏'}
                for choice in choice_list:
                    option = {}
                    option['label'] = choice_dict[choice]
                    option['value'] = choice
                    option['selected'] = False
                    temp['data']['options'].append(option)
                temp['data']['response'] = "我选择的是%label选项"
            message = json.loads(request.body.decode())
            response['msg'] = temp
            response['key'] = attribute
            response['data'] = message
            response = json.dumps(response)
            return HttpResponse(response)
        else:
            answer = str(data[attribute])
            print "选择了：", answer
            if type(choice[0]) == unicode:
                answer = str(answer)
            elif type(choice[0]) == int:
                answer = int(answer)
            if type(tree[attribute][answer]).__name__ == 'dict':
                return Select(request, tree[attribute][answer])
            else:
                print tree[attribute][answer]
                result_index = tree[attribute][answer]
                recommenders = []
                for i in range(len(result_index)):
                    recommender = {}
                    recommender['brand'] = information[result_index[i]][0]
                    recommender['series'] = information[result_index[i]][2]
                    recommender['model'] = information[result_index[i]][1]
                    recommender['url'] = information[result_index[i]][3]
                    #print recommender['url']
                    recommender['image'] = information[result_index[i]][4]
                    text_len, wordcloud = getWordCloud(str(recommender['url']))
                    print text_len, wordcloud
                    if text_len>0:
                        recommender['wordcloud'] = wordcloud
                    recommender['price'] = information[result_index[i]][5]
                    recommenders.append(recommender)
                response = {}
                response['issuer'] = "robot"
                response['type'] = "result"
                response['time'] = datetime.datetime.now().isoformat() + 'Z'
                response['data'] = recommenders
                #response = json.dumps(response)
                response_result = {}
                response_result['msg'] = response
                response_result = json.dumps(response_result)
                return HttpResponse(response_result)
    else:
        return HttpResponse("No POST")

@csrf_exempt
def cluster_select(request):
    message = json.loads(request.body.decode())
    price = str(message['price'])
    weight = message['weight']
    product_index = SelectByWeight(weight, ClusterByPrice(product, price))
    print product_index
    dataSet = np.array(Data(product_index))
    cache = memcache.Client(['127.0.0.1:11211'], debug=True)
    if cache.get('tree') != None:
        tree = cache.get('tree')
        #print tree
    else:
        DT = createDecisionTree(np.array(dataSet), attributes)
        cache.set('tree', DT)
        tree = DT
    return Select(request, tree)
    #return HttpResponse(DT['color'])
