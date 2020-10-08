from django.shortcuts import render
from django.http import HttpResponse
from .models import Blog

# Create your views here.


def blogs_list(request):
    blogs = Blog.objects.all().order_by('date')
    return render(request, 'blogs/blogs_list.html', {'blogs': blogs})


def blog_detail(request, slug):
    blog = Blog.objects.get(slug=slug)
    return render(request, 'blogs/blog_detail.html', {'blog': blog})
