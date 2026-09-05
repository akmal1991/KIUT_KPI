from django.contrib import admin
from django.utils import timezone
from modeltranslation.admin import TranslationAdmin
from .models import Post, PostCoAuthor, Document, AcademicYear

# Register your models here.
# admin.site.register(Post, TranslationAdmin)
admin.site.register(Document)


@admin.register(AcademicYear)
class DriverAdmin(admin.ModelAdmin):
    list_display = ('id', 'years', 'from_date', 'to_date')


@admin.register(Post)
class PostAdmin(TranslationAdmin):
    list_display = ('id', 'title', 'category', 'status', 'estimated_score', 'validated_score')
    search_fields = ['id', 'title', 'title_ru', 'title_en', 'title_uz', 'body']
    list_filter = ['academic_years', 'category__group', 'category', 'teacher', 'status']

    def save_model(self, request, obj, form, change):
        """Reviewing a faculty self-submission (Approve/Reject in this form)
        completes the review trail automatically, so the reviewer only has
        to change status — validated_score defaults to the estimate but stays
        editable for the cases where the reviewer adjusts it (e.g. a
        downgraded quartile)."""
        if change and 'status' in form.changed_data and obj.status in (2, 3):
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
            if obj.status == 2 and obj.validated_score is None:
                obj.validated_score = obj.estimated_score if obj.estimated_score is not None else obj.category.get_coef()
        super().save_model(request, obj, form, change)


@admin.register(PostCoAuthor)
class PostCoAuthorAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'teacher', 'share_percent', 'status', 'requested_at')
    list_filter = ['status']
    search_fields = ['teacher__first_name', 'teacher__last_name', 'post__title']
