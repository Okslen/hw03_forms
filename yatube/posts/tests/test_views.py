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
        cls.test_posts_count = 13
        for i in range(cls.test_posts_count):
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
        """URL-адрес использует соответствующий шаблон"""
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

        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse=reverse):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_views_context(self):
        """Шаблон сформирован с правильным контекстом"""
        id = PostPagesTest.post.id
        views_context_exp = {
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
        views_context = {
            '/': ('title', 'page_obj'),
            '/group/test_slug/': ('page_obj', 'group'),
            '/profile/author/': ('title', 'count', 'page_obj', 'author'),
            f'/posts/{id}/': ('title', 'count', 'post', 'user'),
            f'/posts/{id}/edit/': ('form', 'is_edit', 'post_id', 'groups'),
            '/create/': ('form', 'groups')
        }
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        def form_test(form):
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = form.fields.get(value)
                    self.assertIsInstance(form_field, expected)

        def post_context_test(post):
            post_values = {
                post.text: 'Тестовый пост',
                post.group: PostPagesTest.group,
                post.author: PostPagesTest.author,
            }
            for post_value, expected in post_values.items():
                with self.subTest(post_value=post_value):
                    self.assertEqual(post_value, expected)

        def paginator_test(address, page_obj):
            self.assertEqual(len(page_obj), PER_PAGE)
            response = self.author_client.get(address + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']),
                PostPagesTest.test_posts_count % PER_PAGE,
            )
            post_context_test(page_obj[0])

        for address, context_items in views_context.items():
            response = self.author_client.get(address)
            with self.subTest(context_items=context_items):
                for item in context_items:
                    item_value = response.context.get(item)
                    expected_value = views_context_exp.get(item)
                    self.assertIsInstance(item_value, expected_value)
                    if item == 'form':
                        form_test(item_value)
                    if item == 'post':
                        post_context_test(item_value)
                    if item == 'post_obj':
                        paginator_test(address, item_value)

    def test_post_create(self):
        group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_2',
            description='Тестовое описание 2',
        )
        post = Post.objects.create(
            author=PostPagesTest.author,
            group=group2,
            text='Тестовый пост 2'
        )
        addresses = ('/', '/group/test_slug_2/', '/profile/author/')
        for address in addresses:
            with self.subTest(address=address):
                response = self.author_client.get(address)
                page_obj = response.context.get('page_obj')
                self.assertIn(post, page_obj)
        response = self.author_client.get('/group/test_slug/')
        page_obj = response.context.get('page_obj')
        self.assertNotIn(post, page_obj)
        page_obj = PostPagesTest.group.posts.all()
        self.assertNotIn(post, page_obj)
