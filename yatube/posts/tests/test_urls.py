from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import TestCase, Client
from posts.models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Post.objects.create(
            author=User.objects.create_user(username='auth'),
            group=Group.objects.create(
                title='Тестовая группа',
                slug='test_slug',
                description='Тестовое описание'
            ),
            text='Тестовый пост' * 5
        )

    def setUp(self):
        post = get_object_or_404(Post, pk=1)
        self.guest_client = Client()
        self.user = post.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_exists_at_desired_location(self):
        """Страница доступна любому пользователю"""
        URL_names = ('/', '/group/test_slug/', '/profile/auth/', '/posts/1/')

        for URL_name in URL_names:
            with self.subTest(URL_name=URL_name):
                response = self.guest_client.get(URL_name)
                self.assertEqual(response.status_code, 200)

    def test_url_exists_at_desired_location(self):
        """Страница доступна авторизованному пользователю"""
        URL_names = ('/posts/1/edit/', '/create/')
        for URL_name in URL_names:
            with self.subTest(URL_name=URL_name):
                response = self.authorized_client.get(URL_name)
                self.assertEqual(response.status_code, 200)

    def test_url_exists_at_desired_location(self):
        """Страница перенаправить анонимного пользователя на страницу логина"""
        URL_names = {
            '/posts/1/edit/': '/auth/login/?next=/posts/1/edit/',
            '/create/': '/auth/login/?next=/create/',
        }
        for URL_name, redirect_name in URL_names.items():
            with self.subTest(URL_name=URL_name):
                response = self.guest_client.get(URL_name, follow=True)
                self.assertRedirects(response, redirect_name)
