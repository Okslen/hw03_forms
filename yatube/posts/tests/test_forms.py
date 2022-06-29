from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from posts.models import Group, Post
from posts.forms import PostForm

User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=PostFormTest.author,
            group=PostFormTest.group,
            text='Тестовый пост'
        )
        cls.form = PostForm()

    def setUp(self):
        self.author = PostFormTest.post.author
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_form_create_post(self):
        tasks_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': PostFormTest.group.id
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': f'{PostFormTest.author.username}'}
        ))
        self.assertEqual(Post.objects.count(), tasks_count + 1)

    def test_form_edit_post(self):
        group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_2',
            description='Тестовое описание 2',
        )

        tasks_count = Post.objects.count()
        post = PostFormTest.post
        form_data = {
            'text': 'Измененный тестовый пост',
            'group': group_2.id
        }
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': f'{post.id}'}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            kwargs={'post_id': f'{post.id}'}
        ))
        edit_post = Post.objects.get(id=post.id)
        self.assertEqual(Post.objects.count(), tasks_count)
        self.assertEqual(edit_post.text, form_data['text'])
        self.assertEqual(edit_post.group.id, form_data['group'])
