from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

from .models import Blog, Category, Images


class ImagesInline(admin.TabularInline):
    model = Images
    extra = 0


class BlogAdmin(MarkdownxModelAdmin):
    inlines = [
        ImagesInline,
    ]


admin.site.register(Blog, BlogAdmin)
admin.site.register(Category)
admin.site.register(Images)
