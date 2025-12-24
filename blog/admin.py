from django.contrib import admin
from .models import Blogpost
from django import forms

# Register your models here.
class BlogpostAdminForm(forms.ModelForm):
    class Meta:
        model = Blogpost
        fields = "__all__"
        widgets = {
            "description": forms.Textarea(attrs={"class": "quill-editor"}),
        }

@admin.register(Blogpost)
class BlogpostAdmin(admin.ModelAdmin):
    readonly_fields = ("likes",)
    list_display=("title","author","pub_date","thumbnail")
    list_filter=("pub_date",)
    search_fields=("title","author","description")
    ordering=("-pub_date",)

    def save_model(self, request, obj, form, change):
        if change:
            original = Blogpost.objects.get(pk=obj.pk)
            obj.likes = original.likes
        super().save_model(request, obj, form, change)

    form = BlogpostAdminForm

    class Media:
        css = {
            "all": (
                "https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.snow.css",
                "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css",
                "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css",
                "admin/css/quill-admin.css",
            )
        }
        js = (
            "https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js",
            "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js",

            "https://cdn.jsdelivr.net/npm/quill@1.3.7/dist/quill.min.js",

            "https://cdn.jsdelivr.net/npm/quill-image-resize-module@3.0.0/image-resize.min.js",

            "admin/js/quill-init.js",
        )