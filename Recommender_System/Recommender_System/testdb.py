# -*- coding: utf-8 -*-

from django.http import HttpResponse

from RecommenderApp.models import RecommenderSystem

# 数据库操作
def testdb(request):
    test1 = RecommenderSystem(name='w3cschool.cn')
    test1.save()
    return HttpResponse("<p>数据添加成功！</p>")