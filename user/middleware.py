from django.shortcuts import redirect
from django.urls import reverse

# Paths outside the i18n-prefixed public site (admin, API, static/media, auth
# entry points) — exempt so this redirect can't lock anyone out of them.
EXEMPT_PATH_PREFIXES = ('/static/', '/media/', '/admin/', '/administrator/', '/api/', '/i18n/', '/login/', '/logout/')


class ForcePasswordChangeMiddleware:
    """Redirects a logged-in user with must_change_password=True (set when
    an admin issues a default password for a teacher, see
    user.admin.TeacherAdmin) to the password-change page until they set
    their own password."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, 'user', None)
        if (
            user is not None and user.is_authenticated and getattr(user, 'must_change_password', False)
            and not request.path.startswith(EXEMPT_PATH_PREFIXES)
        ):
            change_password_url = reverse('user_public:password_change')
            if request.path != change_password_url:
                return redirect(change_password_url)
        return self.get_response(request)
