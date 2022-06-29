from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='author'),
            group=Group.objects.create(
                title='Тестовая группа',
                slug='test_slug',
                description='Тестовое описание',
            ),
            text='Тестовый пост' * 5
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='no_author')
        self.author = PostURLTest.post.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_url_exists_at_desired_location(self):
        """Страница доступна любому пользователю, "
        "несуществующая страница вызывает ошибку 404"""
        URL_names = (
            '/',
            '/group/test_slug/',
            '/profile/author/',
            f'/posts/{PostURLTest.post.id}/',
        )
        for URL_name in URL_names:
            with self.subTest(URL_name=URL_name):
                response = self.guest_client.get(URL_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.guest_client.get('/not_exist_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_redirect_not_authorized_user(self):
        """Страница доступна автору и перенаправит других пользователей"""
        id = PostURLTest.post.id
        URL_names = {
            f'/posts/{id}/edit/': f'/auth/login/?next=/posts/{id}/edit/',
            '/create/': '/auth/login/?next=/create/',
        }

        for URL_name, redirect_name in URL_names.items():
            with self.subTest(URL_name=URL_name):
                response = self.author_client.get(URL_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                response_follow = self.guest_client.get(URL_name, follow=True)
                self.assertRedirects(response_follow, redirect_name)
        response = self.authorized_client.get(
            f'/posts/{id}/edit/',
            follow=True
        )
        self.assertRedirects(response, f'/posts/{id}/')

    def test_urls_use_correct_templates(self):
        id = PostURLTest.post.id
        URL_names = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/author/': 'posts/profile.html',
            f'/posts/{id}/': 'posts/post_detail.html',
            f'/posts/{id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for address, template in URL_names.items():
            with self.subTest(template=template):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)
