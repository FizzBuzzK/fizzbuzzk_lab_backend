from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import Blog, BlogImage
from .serializers import (
    SimpleAuthorSerializer,
    UpdateUserProfileSerializer,
    UserInfoSerializer,
    UserRegistrationSerializer,
    BlogSerializer,
)


#================================================
# Pagination
#================================================
class BlogListPagination(PageNumberPagination):
    # default; can be overridden via ?page_size=
    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 50


#================================================
@api_view(["GET"])
def blog_list(request):

    blogs = Blog.objects.all()
    
    paginator = BlogListPagination()
    paginated_blogs = paginator.paginate_queryset(blogs, request)
    
    serializer = BlogSerializer(paginated_blogs, many=True)
    
    return paginator.get_paginated_response(serializer.data)


#================================================
@api_view(["GET"])
def get_keywordinfo(request, keyword):
    
    blogs = Blog.objects.filter(content__icontains=keyword)
    
    paginator = BlogListPagination()
    paginated_blogs = paginator.paginate_queryset(blogs, request)
    
    serializer = BlogSerializer(paginated_blogs, many=True)
    
    return paginator.get_paginated_response(serializer.data)



#================================================
# Get single blog by slug
#================================================
@api_view(["GET"])
def get_blog(request, slug):
    blog = get_object_or_404(
        Blog.objects.select_related("author").prefetch_related("images"),
        slug=slug
    )
    serializer = BlogSerializer(blog)
    return Response(serializer.data, status=status.HTTP_200_OK)


#================================================
@api_view(["POST"])
def register_user(request):

    serializer = UserRegistrationSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





#================================================
# Update own profile
#================================================
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])  # allow profile_picture upload
def update_user_profile(request):
    user = request.user
    partial = request.method == "PATCH"
    serializer = UpdateUserProfileSerializer(user, data=request.data, partial=partial)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#================================================
# Create blog (with multiple images)
#================================================
@api_view(["POST"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])  # needed for featured_image/new_images
def create_blog(request):
    serializer = BlogSerializer(data=request.data)

    if serializer.is_valid():
        blog = serializer.save(author=request.user)  # author from logged-in user
        return Response(BlogSerializer(blog).data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#================================================
# Update blog (partial + multiple images)
#================================================
@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def update_blog(request, pk):
    blog = get_object_or_404(Blog, id=pk)

    if blog.author_id != request.user.id:
        return Response({"error": "You are not the author of this blog"}, status=status.HTTP_403_FORBIDDEN)

    partial = request.method == "PATCH"
    serializer = BlogSerializer(blog, data=request.data, partial=partial)

    if serializer.is_valid():
        blog = serializer.save()  # BlogSerializer handles new_images/remove_image_ids
        return Response(BlogSerializer(blog).data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#================================================
# Delete blog
#================================================
@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_blog(request, pk):
    blog = get_object_or_404(Blog, id=pk)

    if blog.author_id != request.user.id:
        return Response({"error": "You are not the author of this blog"}, status=status.HTTP_403_FORBIDDEN)
    
    blog.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)


#================================================
# Convenience endpoints
#================================================
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_username(request):
    return Response({"username": request.user.username}, status=status.HTTP_200_OK)


#================================================
@api_view(["GET"])
def get_userinfo(request, username):
    User = get_user_model()
    user = get_object_or_404(User, username=username)
    serializer = UserInfoSerializer(user)

    return Response(serializer.data, status=status.HTTP_200_OK)


#================================================
@api_view(["GET"])
def get_user(request, email):
    User = get_user_model()
    user = get_object_or_404(User, email=email)
    serializer = SimpleAuthorSerializer(user)
    
    return Response(serializer.data, status=status.HTTP_200_OK)





