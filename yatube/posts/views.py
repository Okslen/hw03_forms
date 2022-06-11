from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from posts.models import Post, Group, User
from posts.forms import PostForm
from yatube.settings import PER_PAGE


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    context = {
        'title': title,
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_post(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'group': group
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    count = post_list.count()
    paginator = Paginator(post_list, PER_PAGE)
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
    post = get_object_or_404(Post, pk=post_id)
    title = str(post)
    user = post.author
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
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    is_edit = True
    template = 'posts/create_post.html'
    groups = Group.objects.all()
    form = PostForm(instance=post)
    context = {
        'form': form,
        'is_edit': is_edit,
        'post_id': post_id,
        'groups': groups
    }
    if request.method != 'POST':
        return render(request, template, context)
    form = PostForm(request.POST, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.id)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    groups = Group.objects.all()
    form = PostForm()
    context = {
        'form': form,
        'groups': groups
    }
    if request.method != 'POST':
        return render(request, template, context)
    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user.username)
    return render(request, template, context)
