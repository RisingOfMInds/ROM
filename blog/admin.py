from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from markdownx.admin import MarkdownxModelAdmin

from .models import Blog, Category, Images, Author


class ImagesInline(admin.TabularInline):
    model = Images
    extra = 0


class BlogAdmin(MarkdownxModelAdmin):
    inlines = [
        ImagesInline,
    ]

    def get_queryset(self, request):
        qs = super(BlogAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(author=request.user)

    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        obj.save()


class AuthorAdmin(UserAdmin):
    model = Author
    extra = 0

    def get_queryset(self, request):
        qs = super(AuthorAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(id=request.user)


admin.site.register(Blog, BlogAdmin)
admin.site.register(Category)
admin.site.register(Images)
admin.site.register(Author, AuthorAdmin)
