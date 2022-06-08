from django.contrib import admin
from django.apps import AppConfig
from posts.models import Post, Group


class PostConfig(AppConfig):
    name = 'post'


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    list_editable = ('group', )
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'slug',
        'description')
    search_fields = ('title', 'description')
    list_filter = ('title',)
    list_editable = ('title', 'description')
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
