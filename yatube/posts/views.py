from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from posts.models import Post, Group
from posts.forms import PostForm


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    context = {
        'title': title,
        'page_obj': page_obj
    }
    return render(request, template, context)


def groupe_post(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'group': group
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(get_user_model(), username=username)
    post_list = author.posts.all()
    # post_list = Post.objects.filter(author=username)
    count = post_list.count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    title = f'Профайл пользователя {author.get_full_name()}'
    context = {
        'title': title,
        'count': count,
        'page_obj': page_obj,
        'author': author
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = Post.objects.get(pk=post_id)
    title = post.__str__()
    user = get_object_or_404(get_user_model(), username=post.author)
    count = user.posts.all().count()
    context = {
        'title': title,
        'count': count,
        'post': post,
        'user': user
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = Post.objects.get(pk=post_id)
    if post.author == request.user:
        IS_EDIT = True
        template = 'posts/create_post.html'
        groups = Group.objects.all()
        if request.method == 'POST':
            form = PostForm(request.POST, instance=post)
            if form.is_valid():
                form.save()
                return redirect('posts:post_detail', post.id)
        form = PostForm(instance=post)
        context = {'form': form,
                   'is_edit': IS_EDIT,
                   'groups': groups,
                   'post_id': post_id}
        return render(request, template, context)
    return redirect('posts:post_detail', post_id)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    groups = Group.objects.all()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', request.user.username)
    form = PostForm()
    context = {'form': form,
               'groups': groups}
    return render(request, template, context)
