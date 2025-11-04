from django.urls import path
from . import views

app_name = "api"  # optional but recommended for namespacing

#================================================
urlpatterns = [
    
    # Auth / Users
    path("register_user/", views.register_user, name="register_user"),
    path("update_user/", views.update_user_profile, name="update_user"),
    path("get_username/", views.get_username, name="get_username"),
    path("get_userinfo/<str:username>/", views.get_userinfo, name="get_userinfo"),
    path("get_user/<str:email>/", views.get_user, name="get_user"),


    # Blogs
    path("blog_list/", views.blog_list, name="blog_list"),                # GET (paginated, ?q=search)
    path("create_blog/", views.create_blog, name="create_blog"),     # POST (multipart)
    path("blogs/<slug:slug>/", views.get_blog, name="get_blog"),      # GET single by slug
    path("update_blog/<int:pk>/", views.update_blog, name="update_blog"),   # PUT/PATCH (multipart)
    path("delete_blog/<int:pk>/", views.delete_blog, name="delete_blog"),  # DELETE
    path("get_keywordinfo/<str:keyword>", views.get_keywordinfo, name="get_keywordinfo"),

]






