import json
from django.shortcuts import redirect, render
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from .models import Blogpost,Like
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.http import require_POST

# Create your views here.
def index(request):
    myposts=Blogpost.objects.all()
    filterQuery='all'
    return render(request,'blog/index.html',{'myposts':myposts,'filterQuery':filterQuery})

def searchMatch(query,item):
    if query in item.title.lower() or query in item.description.lower() or query in item.author.lower():
        return True
    else:
        return False
def search(request):
    query=request.GET.get('search').lower()
    blogtemp=Blogpost.objects.all()
    blog=[item for item in blogtemp if searchMatch(query,item)]
    params={'allBlogs':blog}
    if len(blog)==0 or len(query)<2:
        messages.error(request,"Match Not Found")
        return redirect('blogHome')
    return render(request,'blog/search.html',params)

def blogpost(request,id):
    post=Blogpost.objects.filter(post_id=id)[0]
    recent_posts = Blogpost.objects.order_by('-pub_date')[:3]
    if request.user.is_authenticated: 
        liked = Like.objects.filter(post=post, user=request.user).exists()
    else:
        messages.warning(request,"Login To Like A Post...")
        liked = False
    return render(request,'blog/blogpost.html',{'post':post,'recent_posts':recent_posts,'liked':liked})

def filters(request):
    filterQuery=request.GET.get('filters')
    if filterQuery=="liked":
        filteredBlogs=Blogpost.objects.order_by('-likes')
    elif filterQuery=="unLiked":
        filteredBlogs=Blogpost.objects.order_by('likes')
    elif filterQuery=="latest":
        filteredBlogs=Blogpost.objects.order_by('-pub_date')
    elif filterQuery=="old":
        filteredBlogs=Blogpost.objects.order_by('pub_date')
    else:
        return redirect("blogHome")
    return render(request,'blog/index.html',{'myposts':filteredBlogs,'filterQuery':filterQuery})

@require_POST
def toggle_like(request):
    data = json.loads(request.body)
    post_id = data.get("post_id")
    post = Blogpost.objects.get(post_id=post_id)
    if request.user.is_authenticated:
        user = request.user

        liked = Like.objects.filter(post=post, user=user).exists()

        if liked:
            Like.objects.filter(post=post, user=user).delete()
            post.likes -= 1
            status = "unliked"
        else:
            Like.objects.create(post=post, user=user)
            post.likes += 1
            status = "liked"

        post.save()

        return JsonResponse({
            "status": status,
            "likes": post.likes
        })
    else:
        status="unknown"
        return JsonResponse({
            "status": status,
            "likes": post.likes
        })

def handleSignup(request):
    if request.method=='POST':
        username=request.POST['username']
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']
        checkUser=User.objects.filter(username=username)
        checkEmail=User.objects.filter(email=email)
        if checkUser.count():
            messages.error(request,"Username Already Exists")
            return redirect('blogHome')
        if checkEmail.count():
            messages.error(request,"Email Already Exists")
            return redirect('blogHome')
        if len(username)>10:
            messages.error(request,"Username Must Be Less Than 10 Character")
            return redirect('blogHome')
        if not username.isalnum():
            messages.error(request,"Username Should Contain Letters And Numbers Only")
            return redirect('blogHome')
        if pass1!=pass2:
            messages.error(request,"Password Do Not Match")
            return redirect('blogHome')
        myuser=User.objects.create_user(username,email,pass1)
        myuser.first_name=fname
        myuser.last_name=lname
        myuser.save()
        messages.success(request,"Your buyCart Account Is Successfully Created")
        user=authenticate(username=username,password=pass1)
        login(request,user)
        return redirect('blogHome')
    else:
        return HttpResponse('404-Not Found')

def handleLogin(request):
    if request.method=='POST':
        loginusername=request.POST['loginusername']
        loginpass=request.POST['loginpass']
        user=authenticate(username=loginusername,password=loginpass)
        if user is not None:
            login(request,user)
            messages.success(request,"Successfully Logged In")
        else:
            messages.error(request,"Invalid Credentials")
        return redirect('blogHome')
    return HttpResponse('404-Not Found')

def handleLogout(request):
    logout(request)
    messages.success(request,"Successfully Logged Out")
    return redirect('blogHome')