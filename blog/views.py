from django.shortcuts import get_object_or_404,render
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count,Q
from .models import Blog,BlogType
from read_statistics.utils import read_statistices_once_read
from user.forms import LoginForm


def get_blog_list_common_data(request,blogs_all_list):
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUMBER)
    page_num = request.GET.get('page', 1)
    page_of_blogs = paginator.get_page(page_num)
    currentr_page_num = page_of_blogs.number  # 获取当前页
    page_range = list(range(max(currentr_page_num - 2, 1), currentr_page_num)) + \
                 list(range(currentr_page_num, min(currentr_page_num + 2, paginator.num_pages) + 1))

    # 省略页码标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    # 首页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    # 尾页
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # 获取博客分类对应的博客数量
    '''
    blog_types = BlogType.objects.filter(is_deleted=False)
    blog_type_list = []
    for blog_type in blog_types:
        blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()
        blog_type_list.append(blog_type)
    '''

    blog_type_list = BlogType.objects.filter(is_deleted=False).annotate(blog_count=Count('blog',filter=Q(blog__is_deleted=False)))

    # 获取日期分类对应的博客数量
    blog_dates = Blog.objects.dates('create_time', 'month', order='DESC').filter(is_deleted=False)
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(create_time__year=blog_date.year,
                                         create_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count

    context = {}
    context['page_of_blogs'] = page_of_blogs
    context['blog_types'] = blog_type_list
    context['page_range'] = page_range
    context['blogs'] = blogs_all_list
    context['blog_dates'] = blog_dates_dict
    return context

def blog_list(request):
    blogs_all_list = Blog.objects.filter(is_deleted=False,blog_type__is_deleted=False)
    context = get_blog_list_common_data(request,blogs_all_list)
    return render(request, 'blog/blog_list.html', context)

def blogs_with_list(request,blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk,is_deleted=False)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type,is_deleted=False)

    context = get_blog_list_common_data(request,blogs_all_list)
    context['blog_type'] = blog_type
    return render(request, 'blog/blogs_with_list.html', context)

def blogs_with_date(request,year,month):
    blogs_all_list = Blog.objects.filter(create_time__year=year,create_time__month=month)
    context = get_blog_list_common_data(request,blogs_all_list)
    context['blogs_with_date'] = '%s年%s月'%(year,month)
    return render(request, 'blog/blogs_with_date.html', context)

def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog,pk=blog_pk,is_deleted=False)
    read_cookie_key = read_statistices_once_read(request,blog)

    context = {}
    context['blog'] = blog
    context['previous_blog'] = Blog.objects.filter(create_time__gt=blog.create_time,is_deleted=False).last()
    context['next_blog'] = Blog.objects.filter(create_time__lt=blog.create_time,is_deleted=False).first()
    context['blogTypes'] = BlogType.objects.filter(is_deleted=False)
    response = render(request, 'blog/blog_detail.html', context)
    response.set_cookie(read_cookie_key,'true',max_age=600)
    return response