from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils.text import slugify


#================================================
# Users 
#================================================
class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True)

    # Stores an uploaded file managed by Django storage (e.g., local, S3)
    profile_picture = models.ImageField(
        upload_to="profile_img",
        blank=True, null=True,
        default="profile_img/profile_pic.png"
    )

    # Stores a plain URL string (use if avatar is hosted elsewhere/CDN)
    profile_picture_url = models.URLField(blank=True, null=True)

    facebook = models.URLField(max_length=255, blank=True, null=True)
    youtube = models.URLField(max_length=255, blank=True, null=True)
    instagram = models.URLField(max_length=255, blank=True, null=True)
    twitter = models.URLField(max_length=255, blank=True, null=True)
    linkedin = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.username


#================================================
# Blogs 
#================================================
def blog_image_upload_to(instance, filename):
    # Files end up under blog_img/<blog_id>/<filename>
    # (instance.blog_id is available because BlogImage is saved after Blog)
    return f"blog_img/{instance.blog_id}/{filename}"


#================================================
# Single Blog
#================================================
class Blog(models.Model):
    CATEGORY = (
        ("Full Stack/Software Engineering", "Full Stack/Software Engineering"),
        ("ML/Data Science", "ML/Data Science"),
        ("Data Analytics", "Data Analytics"),
        ("AI", "AI"),
    )
    LANGUAGE = (
        ("Python", "Python"),
        ("JavaScript", "JavaScript"),
        ("Java", "Java"),
        ("SQL", "SQL"),
    )

    headline = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    content = models.TextField()

    # Best practice: reference AUTH_USER_MODEL
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="blogs",
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=255, choices=CATEGORY, blank=True, null=True)

    # Keep a single featured/cover image if you like
    featured_image = models.ImageField(upload_to="blog_featured", blank=True, null=True)

    language = models.CharField(max_length=255, choices=LANGUAGE, blank=True, null=True)

    # Optional: draft/publish flag (you had a comment referring to this)
    is_draft = models.BooleanField(default=True)


    #================================================
    # up to three links to Live App/LinkedIn/GitHub
    #================================================
    web_app_link_1 = models.URLField("Web app link 1", max_length=500, blank=True, null=True)
    web_app_link_2 = models.URLField("Web app link 2", max_length=500, blank=True, null=True)
    web_app_link_3 = models.URLField("Web app link 3", max_length=500, blank=True, null=True)

    
    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.headline

    def save(self, *args, **kwargs):
        # Only generate slug once (don’t change on edit to avoid breaking URLs)
        if not self.slug:
            base = slugify(self.headline) or "post"
            candidate = base
            i = 1
            while Blog.objects.filter(slug=candidate).exists():
                candidate = f"{base}-{i}"
                i += 1
            self.slug = candidate
        super().save(*args, **kwargs)



#================================================
# Images for carousels in blog post
#================================================
class BlogImage(models.Model):
    """
    Additional images for a blog post (one-to-many).
    Use this for carousels/galleries on the React side.
    """
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(upload_to=blog_image_upload_to)
    caption = models.CharField(max_length=255, blank=True, null=True)
    alt_text = models.CharField(max_length=255, blank=True, null=True)

    # Optional: control display order
    order = models.PositiveIntegerField(default=0)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "id"]
        constraints = [
            # Prevent duplicate "order" values per blog (helps sortable UI)
            models.UniqueConstraint(
                fields=["blog", "order"], name="unique_image_order_per_blog"
            )
        ]

    def __str__(self):
        return f"Image #{self.pk} for {self.blog.headline}"




