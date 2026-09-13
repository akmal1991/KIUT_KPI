import secrets
import string

from django import forms
from django.contrib import admin
from django.contrib.auth.hashers import make_password

# Register your models here.
from modeltranslation.admin import TranslationAdmin

from post.models import Post
from user.models import User, Division, Teacher, ControlLimit, TeacherLevel, AcademicLevel, Target
from django.contrib.auth.admin import UserAdmin


def _generate_default_username():
    return 'teacher_' + secrets.token_hex(3)


def _generate_default_password():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(10))


class PostInline(admin.StackedInline):
    model = Post
    extra = 0
    fields = ('title', 'status', 'category')


class TeacherAdminForm(forms.ModelForm):
    """Adds login-credential fields so creating a Teacher also provisions
    their login: a username and a default password they're forced to
    change on first login (see user.middleware.ForcePasswordChangeMiddleware)."""

    username = forms.CharField(
        max_length=150, required=False,
        help_text="Login username for this teacher. Edit the generated default if you like.",
    )
    password = forms.CharField(
        max_length=128, required=False,
        help_text="Default password handed to the teacher; they're forced to change it on first login.",
    )

    class Meta:
        model = Teacher
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        existing_user = getattr(self.instance, 'user_account', None) if self.instance.pk else None
        if existing_user is None:
            self.fields['username'].initial = _generate_default_username()
            self.fields['password'].initial = _generate_default_password()
        else:
            self.fields['username'].initial = existing_user.username
            self.fields['username'].help_text = 'Existing login username for this teacher.'
            self.fields['password'].help_text = (
                'Leave blank to keep the current password, or set one to reset it '
                '(the teacher will be forced to change it on next login).'
            )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not username:
            return username
        existing_user = getattr(self.instance, 'user_account', None) if self.instance.pk else None
        conflicting = User.objects.filter(username=username)
        if existing_user is not None:
            conflicting = conflicting.exclude(pk=existing_user.pk)
        if conflicting.exists():
            raise forms.ValidationError('This username is already taken.')
        return username


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    form = TeacherAdminForm
    inlines = [PostInline]
    list_display = ('id', 'first_name', 'last_name', 'father_name')
    search_fields = ['id', 'first_name', 'last_name', 'father_name']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        existing_user = getattr(obj, 'user_account', None)

        if existing_user is None:
            if username:
                User.objects.create(
                    username=username,
                    # A leftover unique constraint on email predates this feature (from a
                    # reverted migration never rolled back); a synthetic per-account
                    # address avoids colliding with it without touching that schema.
                    email=f'{username}@kiut.local',
                    password=make_password(password or _generate_default_password()),
                    role=User.Role.FACULTY,
                    teacher_profile=obj,
                    must_change_password=True,
                )
        else:
            update_fields = []
            if username and username != existing_user.username:
                existing_user.username = username
                update_fields.append('username')
            if password:
                existing_user.password = make_password(password)
                existing_user.must_change_password = True
                update_fields.extend(['password', 'must_change_password'])
            if update_fields:
                existing_user.save(update_fields=update_fields)


@admin.register(User)
class KiutUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('role',)
    list_filter = UserAdmin.list_filter + ('role',)
    fieldsets = UserAdmin.fieldsets + (
        ('KIUT role', {
            'fields': ('role', 'teacher_profile', 'division', 'father_name', 'image', 'birth', 'phone'),
        }),
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
