from django.contrib import admin

# Register your models here.
from modeltranslation.admin import TranslationAdmin

from post.models import Post
from user.models import User, Division, Teacher, ControlLimit, TeacherLevel, AcademicLevel, Target, EmailOTP
from django.contrib.auth.admin import UserAdmin


class PostInline(admin.StackedInline):
    model = Post
    extra = 0
    fields = ('title', 'status', 'category')


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    inlines = [PostInline]
    list_display = ('id', 'first_name', 'last_name', 'father_name')
    search_fields = ['id', 'first_name', 'last_name', 'father_name']


@admin.register(User)
class KiutUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('role', 'status')
    list_filter = UserAdmin.list_filter + ('role', 'status')
    fieldsets = UserAdmin.fieldsets + (
        ('KIUT role', {
            'fields': ('role', 'status', 'teacher_profile', 'division', 'father_name', 'image', 'birth', 'phone'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('KIUT role', {'fields': ('role', 'status')}),
    )


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    """Read-only: codes are hashed and issuance/verification must go through
    the API (EmailOTP.issue / check_code) so attempt-count and expiry stay
    authoritative — never edited by hand."""
    list_display = ('user', 'is_used', 'attempts', 'expires_at', 'created')
    list_filter = ('is_used',)
    search_fields = ('user__email', 'user__username')
    readonly_fields = [f.name for f in EmailOTP._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(Division, TranslationAdmin)
admin.site.register(ControlLimit)
admin.site.register(TeacherLevel, TranslationAdmin)
admin.site.register(AcademicLevel, TranslationAdmin)


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created')
    search_fields = ('name', 'created')
