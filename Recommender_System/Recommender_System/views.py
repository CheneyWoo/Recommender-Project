from django.http import HttpResponse, Http404
from django.shortcuts import render
import datetime

def hello(request):
    context = {}
    context['hello'] = 'Hello World!'
    #return HttpResponse("Hello world!")
    return render(request, 'test.html', context)

def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

def hours_ahead(request, offset):
    try:
        offset = int(offset)
    except ValueError:
        raise Http404()
    dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
    html = "<html><body>In %s hour(s), it will be %s.</body></html>" % (offset, dt)
    return HttpResponse(html)