from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import AbstractUser
from django.utils.safestring import mark_safe
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


class AuthorAdmin(admin.ModelAdmin):

    def get_queryset(self, request):
        qs = super(AuthorAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(id=request.user.id)

    def get_exclude(self, request, obj=None):
        excluded = super().get_exclude(request, obj) or []  # get overall excluded fields

        if not request.user.is_superuser:  # if user is not a superuser
            return excluded + ['last_login', 'is_superuser', 'is_staff', 'date_joined', 'user_permissions', 'groups',
                               'is_active']

        return excluded

    def save_model(self, request, obj, form, change):
        if obj.pk:
            orig_obj = Author.objects.get(pk=obj.pk)
            if obj.password != orig_obj.password:
                obj.set_password(obj.password)
        else:
            obj.set_password(obj.password)
        obj.save()


admin.site.register(Blog, BlogAdmin)
admin.site.register(Category)
admin.site.register(Images)
admin.site.register(Author, AuthorAdmin)
