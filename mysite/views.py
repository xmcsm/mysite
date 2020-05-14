import datetime
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache
from blog.models import Blog
from read_statistics.utils import get_seven_days_read_data,get_today_hot_data,get_yesterday_hot_data


def get_seven_day_hot_data():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects.filter(read_detail__date__lt=today,read_detail__date__gte=date)\
        .values('pk','title')\
        .annotate(read_num_sum=Sum('read_detail__read_num')).order_by('-read_num_sum')
    return blogs[:10]

def index(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    read_nums,dates = get_seven_days_read_data(blog_content_type)

    # 获取7天热门博客的缓存数据
    sevenday_hot_data = cache.get('sevenday_hot_data')
    if sevenday_hot_data is None:
        sevenday_hot_data = get_seven_day_hot_data()
        cache.set('sevenday_hot_data',get_seven_day_hot_data,3600)


    context = {}
    context['read_nums'] = read_nums
    context['dates'] = dates
    context['today_hot_data'] = get_today_hot_data(blog_content_type)
    context['yesterday_hot_data'] = get_yesterday_hot_data(blog_content_type)
    context['sevenday_hot_data'] = sevenday_hot_data
    return render(request,'index.html',context)
