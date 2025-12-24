from django.urls import path
from . import views

urlpatterns = [
    path("", views.index,name="blogHome"),
    path("blogpost/<int:id>", views.blogpost,name="blogPost"),
    path("search/",views.search,name="Search"),
    path("filtered/",views.filters,name="Filter"),
    path('signup/',views.handleSignup,name='handleSignup'),
    path('login/',views.handleLogin,name='handleLogin'),
    path('logout/',views.handleLogout,name='handleLogout'),
    path('toggle-like/',views.toggle_like,name='toggleLike'),
]