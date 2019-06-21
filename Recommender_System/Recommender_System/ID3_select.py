# -*- coding:utf-8 -*-
from cluster_select import dataframe
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
import math
import pandas as pd
import numpy as np

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
    #print labelSet
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
    #print labelSet
    #计算熵值
    for key in labelSet:
        pi = float(labelSet[key])/totalNum
        Ent -= pi*math.log(pi,2)
    #print labelSet
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
    featNum = len(dataSet[0]) - 1
    maxEnt = 0
    bestFeat = -1
    #以每一个特征进行分类，找出信息熵最大的特征
    for i in range(featNum):
        #print labelSet[i],"的所有属性值",featList
        Ent = calcEnt(dataSet,i)
        print labelSet[i],Ent
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
    del featName[bestFeat]
    #以字典形式表示树
    DTree = {bestFeatName:{}}
    #根据选择的特征，遍历该特征的所有属性值，在每个划分子集上递归调用createDecisionTree
    print bestFeat
    featValue = [dataVec[bestFeat] for dataVec in dataSet]
    featValue = set(featValue)
    #print featValue
    #print "剩余候选属性是", featName
    for value in featValue:
        subFeatName = featName[:]
        DTree[bestFeatName][value] = createDecisionTree(splitDataSet(dataSet,bestFeat,value), subFeatName)
    return DTree

#实例化决策树
#dataSet = np.array(Data(product_index))
#DT = createDecisionTree(np.array(dataSet),attributes)
#print DT

#模拟选择过程
def Select(tree):
    attribute = tree.keys()[0]
    choice = tree[attribute].keys()
    print "当前属性", attribute
    print "可供选择选项", choice
    answer = raw_input("Your choice is:")
    if type(choice[0]) == unicode:
        answer = str(answer)
    elif type(choice[0]) == int:
        answer = int(answer)
    if type(tree[attribute][answer]).__name__ == 'dict':
        Select(tree[attribute][answer])
    else:
        print tree[attribute][answer]


