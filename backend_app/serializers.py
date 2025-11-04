from rest_framework import serializers
from django.contrib.auth import get_user_model

from .models import Blog, BlogImage


#================================================
# Users
#================================================
class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "password", "profile_picture"
        ]
        extra_kwargs = {
            "password": {"write_only": True},
            "profile_picture": {"required": False, "allow_null": True},
            "email": {"required": True},
            "username": {"required": True},
        }

    def create(self, validated_data):
        User = get_user_model()
        password = validated_data.pop("password")
        user = User.objects.create_user(password=password, **validated_data)
        return user


#================================================
class UpdateUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            "id", "email", "username", "first_name", "last_name", "bio",
            "profile_picture",
            "facebook", "youtube", "instagram", "twitter", "linkedin",
        ]
        extra_kwargs = {
            "email": {"required": False},
            "username": {"required": False},
            "profile_picture": {"required": False, "allow_null": True},
        }


#================================================
# Minimal author for embedding in posts
class SimpleAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["id", "username", "first_name", "last_name", "email", "profile_picture"]


#================================================
# Blogs & Images
#================================================
class BlogImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogImage
        fields = ["id", "image", "caption", "alt_text", "order", "uploaded_at"]
        read_only_fields = ["id", "uploaded_at"]


#================================================
class BlogSerializer(serializers.ModelSerializer):
    author = SimpleAuthorSerializer(read_only=True)
    images = BlogImageSerializer(many=True, read_only=True)

    new_images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False, use_url=False),
        write_only=True,
        required=False,
    )
    remove_image_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        write_only=True,
        required=False,
    )

    class Meta:
        model = Blog
        fields = [
            "id", "headline", "slug", "author",
            "category", "language", "content",
            "featured_image", "created_at",
            "web_app_link_1", "web_app_link_2", "web_app_link_3",
            "images",          # read-only list
            "new_images",      # write-only list of files
            "remove_image_ids" # write-only list of ints
        ]
        read_only_fields = ["id", "slug", "author", "created_at"]
        extra_kwargs = {
            "featured_image": {"required": False, "allow_null": True},
            "category": {"required": False, "allow_null": True},
            "language": {"required": False, "allow_null": True},
            "web_app_link_1": {"required": False, "allow_null": True, "allow_blank": True},
            "web_app_link_2": {"required": False, "allow_null": True, "allow_blank": True},
            "web_app_link_3": {"required": False, "allow_null": True, "allow_blank": True},
        }

    # Optional: normalize links to include scheme if missing
    def validate(self, attrs):
        for key in ("web_app_link_1", "web_app_link_2", "web_app_link_3"):
            val = attrs.get(key)
            if val:
                s = val.strip()
                if s and not s.lower().startswith(("http://", "https://")):
                    s = "https://" + s
                attrs[key] = s
        return super().validate(attrs)

    def create(self, validated_data):
        new_images = validated_data.pop("new_images", [])
        blog = super().create(validated_data)
        for idx, img in enumerate(new_images):
            BlogImage.objects.create(blog=blog, image=img, order=idx)
        return blog

    def update(self, instance, validated_data):
        new_images = validated_data.pop("new_images", [])
        remove_ids = validated_data.pop("remove_image_ids", [])
        blog = super().update(instance, validated_data)

        if remove_ids:
            BlogImage.objects.filter(blog=blog, id__in=remove_ids).delete()

        start_order = (
            BlogImage.objects.filter(blog=blog).order_by("-order").first().order + 1
            if BlogImage.objects.filter(blog=blog).exists() else 0
        )
        for i, img in enumerate(new_images):
            BlogImage.objects.create(blog=blog, image=img, order=start_order + i)

        return blog


#================================================
class UserInfoSerializer(serializers.ModelSerializer):
    author_posts = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            "id", "username", "email",
            "first_name", "last_name",
            "bio", "profile_picture",
            "author_posts",
        ]

    def get_author_posts(self, user):
        blogs = Blog.objects.filter(author=user)[:12]
        serializer = BlogSerializer(blogs, many=True)
        return serializer.data









