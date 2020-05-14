import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from .models import ReadNum,ReadDetail


def read_statistices_once_read(request,obj):
    ct = ContentType.objects.get_for_model(obj)
    key = '%s_%s_read' %(ct.model,obj.pk)
    # 阅读计数
    if not request.COOKIES.get(key):
        readnum,created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        readnum.read_num += 1
        readnum.save()

        date = timezone.now().date()
        readdetail,created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=date)
        readdetail.read_num += 1
        readdetail.save()
    return key

def get_seven_days_read_data(content_type):
    today = timezone.now().date()
    dates = []
    read_nums = []
    for i in range(7,0,-1):
        date =  today - datetime.timedelta(days=i)
        dates.append(date.strftime('%m/%d'))
        read_deatils = ReadDetail.objects.filter(content_type=content_type,date=date)
        result = read_deatils.aggregate(read_num_sum=Sum('read_num'))
        read_nums.append(result['read_num_sum'] or 0)
    return read_nums,dates

def get_today_hot_data(content_type):
    today = timezone.now().date()
    read_deatils = ReadDetail.objects.filter(content_type=content_type,date=today).order_by('-read_num')
    return read_deatils[:10]

def get_yesterday_hot_data(content_type):
    today = timezone.now().date()
    yesterday = today - datetime.timedelta(days=1)
    read_deatils = ReadDetail.objects.filter(content_type=content_type,date=yesterday).order_by('-read_num')
    return read_deatils[:10]

def get_seven_day_hot_data(content_type):
    today = timezone.now().date()
    date = today - datetime.timedelta(days=6)
    read_deatils = ReadDetail.objects\
        .filter(content_type=content_type,date__lt=today,date__gt=date)\
        .values('content_type','object_id')\
        .annotate(read_num_sum=Sum('read_num'))\
        .order_by('-read_num_sum')
    return read_deatils