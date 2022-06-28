from django import forms
from django.contrib.auth import get_user_model
from django.core.paginator import Page
from django.db.models.query import QuerySet
from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Group, Post
from posts.forms import PostForm
from yatube.settings import PER_PAGE


User = get_user_model()
test_posts_count = 13


class PostPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        for i in range(test_posts_count):
            cls.post = Post.objects.create(
                author=PostPagesTest.author,
                group=PostPagesTest.group,
                text='Тестовый пост'
            )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='no_author')
        self.author = PostPagesTest.post.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_views_template_and_forms(self):
        """URL-адрес использует соответствующий шаблон, поле формы"""
        post = PostPagesTest.post
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={"slug": f'{post.group.slug}'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': f'{post.author.username}'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{post.id}'}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{post.id}'}
            ): 'posts/create_post.html',
        }
        views_context = {
            'title': str,
            'page_obj': Page,
            'group': Group,
            'count': int,
            'author': User,
            'post': Post,
            'user': User,
            'form': PostForm,
            'is_edit': bool,
            'post_id': int,
            'groups': QuerySet
        }
        form_fields = {
            'pub_date': forms.fields.DateTimeField,
            'text': forms.fields.CharField,
            'title': forms.fields.CharField,
            'slug': forms.fields.SlugField,
            'description': forms.fields.CharField,
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse=reverse):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
                for value, expected in views_context.items():
                    with self.subTest(value=value):
                        context_value = response.context.get(value)
                        if context_value:
                            self.assertIsInstance(context_value, expected)
                        if context_value == 'form':
                            for form_field, exp_field in form_fields:
                                with self.subTest(form_field=form_field):
                                    form = context_value.fields.get(form_field)
                                    self.assertIsInstance(form, exp_field)

    def test_paginator_views(self):
        post = PostPagesTest.post

        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={"slug": f'{post.group.slug}'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': f'{post.author.username}'}
            ): 'posts/profile.html',
        }

        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse=reverse):
                response = self.author_client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    test_posts_count % PER_PAGE,
                )
                response = self.author_client.get(reverse_name)
                page_obj = response.context['page_obj']
                self.assertEqual(len(page_obj), PER_PAGE)
                post = page_obj[0]
                post_values = {
                    post.text: 'Тестовый пост',
                    post.group: PostPagesTest.group,
                    post.author: PostPagesTest.author,
                }
                for post_value, expected in post_values.items():
                    with self.subTest(post_value=post_value):
                        self.assertEqual(post_value, expected)
