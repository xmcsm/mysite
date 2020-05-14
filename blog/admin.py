from django.contrib import admin

from .models import BlogType,Blog

@admin.register(BlogType)
class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ('id','type_name','is_deleted')

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('id','title','blog_type','author','get_read_num','create_time','update_time','is_deleted')

'''
@admin.register(ReadNum)
class ReadNumAdmin(admin.ModelAdmin):
    list_display = ('id','read_num','blog')
    
'''

