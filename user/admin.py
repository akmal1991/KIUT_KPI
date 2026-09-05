from django.contrib import admin

# Register your models here.
from modeltranslation.admin import TranslationAdmin

from post.models import Post
from user.models import User, Division, Teacher, ControlLimit, TeacherLevel, AcademicLevel, Target
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
    list_display = UserAdmin.list_display + ('role',)
    list_filter = UserAdmin.list_filter + ('role',)
    fieldsets = UserAdmin.fieldsets + (
        ('KIUT role', {'fields': ('role', 'division', 'father_name', 'image', 'birth', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('KIUT role', {'fields': ('role',)}),
    )
admin.site.register(Division, TranslationAdmin)
admin.site.register(ControlLimit)
admin.site.register(TeacherLevel, TranslationAdmin)
admin.site.register(AcademicLevel, TranslationAdmin)


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created')
    search_fields = ('name', 'created')
