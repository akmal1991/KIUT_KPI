from user.models import AcademicLevel, Division, TeacherLevel


def faculty_registration_options(request):
    """Feeds the faculty self-registration modal (rendered site-wide in
    base_public.html) its dropdown options, regardless of which view rendered
    the current page."""
    return {
        'division_list': Division.objects.all(),
        'academic_level_list': AcademicLevel.objects.all(),
        'teacher_level_list': TeacherLevel.objects.all(),
    }
