from django.contrib import admin
from modeltranslation.admin import TranslationAdmin
from .models import Post, Document, AcademicYear

# Register your models here.
# admin.site.register(Post, TranslationAdmin)
admin.site.register(Document)


@admin.register(AcademicYear)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('id', 'years', 'from_date', 'to_date')


@admin.register(Post)
class PostAdmin(TranslationAdmin):
    list_display = ('id', 'title', 'category')
    search_fields = ['id', 'title', 'title_ru', 'title_en', 'title_uz', 'body']
    list_filter = ['academic_years', 'category__group', 'category', 'teacher']
