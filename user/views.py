import datetime

from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import PasswordChangeView
from django.db.models import Q, Sum
from django.urls import reverse_lazy
from django.views import generic

from post.models import Document, Post, AcademicYear
from post.review import reviewer_visible_posts
from user.models import Teacher, Division, TeacherLevel, AcademicLevel, User
from category.models import Category


# Create your views here.

# //////////////////////////// Administrator views ///////////////////////////////

class DivisionAdminListView(LoginRequiredMixin, generic.ListView):
    paginate_by = 12
    model = Division
    queryset = Division.objects.all()
    template_name = 'administrator/division/list.html'


class TeacherAdminListView(LoginRequiredMixin, generic.ListView):
    model = Teacher
    queryset = Teacher.objects.all().order_by('last_name', 'first_name', 'father_name')
    paginate_by = 15
    template_name = 'administrator/teacher/list.html'

    def get_queryset(self):
        teachers = Teacher.objects.all().order_by('last_name', 'first_name', 'father_name')
        if self.request.GET.get('limit_by_year'):
            category_id = self.request.GET.get('category')
            teachers = Teacher.teachers_exceeding_category_limits(self.request.GET.get('limit_by_year'), category_id)
        if self.request.GET.get('name'):
            name = self.request.GET.get('name')
            teachers = teachers.filter(
                Q(first_name__icontains=name) |
                Q(last_name__icontains=name) |
                Q(father_name__contains=name) |
                Q(position__contains=name) |
                Q(uuid__icontains=name) |

                Q(first_name_ru__icontains=name) |
                Q(last_name_ru__icontains=name) |
                Q(father_name_ru__contains=name) |
                Q(position_ru__contains=name) |

                Q(first_name_en__icontains=name) |
                Q(last_name_en__icontains=name) |
                Q(father_name_en__contains=name) |
                Q(position_en__contains=name) |

                Q(first_name_uz__icontains=name) |
                Q(last_name_uz__icontains=name) |
                Q(father_name_uz__contains=name) |
                Q(position_uz__contains=name)
            )
        if self.request.GET.get('level'):
            level = self.request.GET.get('level')
            teachers = teachers.filter(level__id=level)

        if self.request.GET.get('division'):
            division = self.request.GET.get('division')
            teachers = teachers.filter(division__id=division)

        if self.request.GET.get('select-status'):
            teachers = teachers.filter(status=self.request.GET.get('select-status'))

        return teachers

    def get_context_data(self, *, object_list=None, **kwargs):
        if self.request.GET.get('limit_by_year'):
            academic_year_id = self.request.GET.get('limit_by_year')
        else:
            academic_year_id = AcademicYear.get_current_academic_year().id
        context = super(TeacherAdminListView, self).get_context_data(**kwargs)
        context['limit_by_year'] = academic_year_id
        context['teacher_level_list'] = TeacherLevel.objects.all()
        context['teacher_academic_level_list'] = AcademicLevel.objects.all()
        context['academic_years'] = AcademicYear.objects.all()
        context['division_list'] = Division.objects.all()
        context['teacher_limit_count'] = Teacher.teachers_exceeding_category_limits(academic_year_id).count()
        context['category_list'] = Category.objects.all()
        return context


class TeacherAdminDetailView(LoginRequiredMixin, generic.DetailView):
    model = Teacher
    queryset = Teacher.objects.all()
    template_name = 'administrator/teacher/detail.html'

    def get_limit_category_posts(self, academic_year, category_id=None):
        posts_queryset = self.object.post_set.none()
        categories = Category.objects.filter(post__teacher=self.object, limit__isnull=False).distinct()
        if category_id:
            categories = Category.objects.filter(id=category_id, limit__isnull=False)
        for category in categories:
            posts = self.object.post_set.filter(academic_years=academic_year, category=category)
            if posts.count() > category.limit:
                posts_queryset = posts_queryset.union(posts)

        return posts_queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        if self.request.GET.get('academic_year'):
            cur_aca_year = self.request.GET.get('academic_year')
            current_academic_year = AcademicYear.objects.filter(id=int(cur_aca_year)).last()
        else:
            current_academic_year = AcademicYear.get_current_academic_year()

        context = super(TeacherAdminDetailView, self).get_context_data(**kwargs)
        context['teacher_list'] = Teacher.objects.all()
        post_list = self.object.post_set.filter(academic_years=current_academic_year).order_by('-date')

        category_id = self.request.GET.get('category')
        if category_id:
            post_list = post_list.filter(category__id=category_id)

        if self.request.GET.get('limit'):
            if category_id:
                post_list = self.get_limit_category_posts(current_academic_year, category_id)
            else:
                post_list = self.get_limit_category_posts(current_academic_year)

        context['post_list'] = post_list

        context['academic_years'] = AcademicYear.objects.all()
        context['current_academic_year'] = current_academic_year

        context['categories'] = []
        for category in Category.objects.filter(post__teacher=self.object).distinct():
            context['categories'].append({
                'category': category,
                'count': category.post_set.filter(teacher=self.object).count,
                'limit': self.object.get_limit_category(category, current_academic_year)
            })

        context['category_list'] = []
        for category in Category.objects.filter(post__teacher=self.object,
                                                post__academic_years=current_academic_year).distinct():
            context['category_list'].append({
                'category': category,
                'count': category.post_set.filter(teacher=self.object, academic_years=current_academic_year).count,
                'limit': self.object.get_limit_category(category, current_academic_year)
            })

        context['teacher_level_list'] = TeacherLevel.objects.all()
        context['teacher_academic_level_list'] = AcademicLevel.objects.all()
        context['division_list'] = Division.objects.all()
        return context


class TeacherLevelAdminListView(LoginRequiredMixin, generic.ListView):
    paginate_by = 12
    model = TeacherLevel
    queryset = TeacherLevel.objects.all()
    template_name = 'administrator/level/list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TeacherLevelAdminListView, self).get_context_data(**kwargs)
        context['professor_count'] = Teacher.objects.filter(position='профессор'.lower()).count()
        return context


class UserAccountAdminListView(LoginRequiredMixin, generic.ListView):
    """Assigns roles (e.g. Department/Scientific Reviewer) to existing login
    accounts. Accounts themselves are provisioned elsewhere: via the Add
    Teacher modal (user.admin / api.v1.user for teacher-linked accounts) or
    Django's built-in /admin/ for standalone ones."""

    model = User
    queryset = User.objects.all().order_by('username')
    paginate_by = 20
    template_name = 'administrator/user/list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['division_list'] = Division.objects.all()
        return context


# ///////////////////////////////////////////////////////////////////////

class TeacherPublicListView(generic.ListView):
    template_name = 'public/teacher/list.html'
    model = Teacher
    paginate_by = 12

    def get_queryset(self):
        teachers = Teacher.objects.exclude(status=3)
        today = datetime.date.today()
        academic_id = self.request.GET.get('academic_year')
        if academic_id:
            academic_year = AcademicYear.objects.filter(id=int(academic_id)).last()
        else:
            academic_year = AcademicYear.objects.filter(
                from_date__lte=today, to_date__gte=today).last()

        start_date = academic_year.from_date
        end_date = academic_year.to_date
        teachers = teachers.filter(
            Q(post__date__gte=start_date) & Q(post__date__lte=end_date) | Q(post__category__id=29))
        # sorted(teachers, key=lambda t: t.get_total_ball())
        if self.request.GET.get('division'):
            teachers = teachers.filter(division=self.request.GET.get('division'))
        if self.request.GET.get('uuid'):
            teachers = teachers.filter(uuid=self.request.GET.get('uuid'))
        if self.request.GET.get('level'):
            teachers = teachers.filter(level=self.request.GET.get('level'))
        if self.request.GET.get('name'):
            name = self.request.GET.get('name')
            teachers = teachers.filter(Q(first_name__icontains=name) |
                                       Q(last_name__icontains=name) |
                                       Q(father_name__contains=name))
        approved_only = Q(post__status=2)
        if self.request.GET.get('order_by') == 'ball_asc':
            return teachers.annotate(total_ball=Sum('post__category__coef', filter=approved_only)).order_by(
                'total_ball')
        if self.request.GET.get('order_by') == 'ball_desc':
            return teachers.annotate(total_ball=Sum('post__category__coef', filter=approved_only)).order_by(
                '-total_ball')
        return teachers.annotate(total_ball=Sum('post__category__coef', filter=approved_only)).order_by(
            'last_name', 'first_name', 'father_name', '-total_ball')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(TeacherPublicListView, self).get_context_data(**kwargs)
        context['division_list'] = Division.objects.all()
        context['teacher_level_list'] = TeacherLevel.objects.all()
        context['academic_year_list'] = AcademicYear.objects.all()
        today = datetime.date.today()
        current_academic_year = AcademicYear.objects.filter(
            from_date__lte=today, to_date__gte=today).last()
        context['current_academic_year'] = current_academic_year.id

        return context


class TeacherPublicDetailView(generic.DetailView):
    template_name = 'public/teacher/detail.html'
    model = Teacher

    def get_context_data(self, *, object_list=None, **kwargs):
        if self.request.GET.get('academic_year'):
            cur_aca_year = self.request.GET.get('academic_year')
            current_academic_year = AcademicYear.objects.filter(id=int(cur_aca_year)).last()
        else:
            current_academic_year = AcademicYear.get_current_academic_year()

        context = super(TeacherPublicDetailView, self).get_context_data(**kwargs)
        context['teacher_list'] = Teacher.objects.all()
        context['post_list'] = self.object.post_set.filter(academic_years=current_academic_year).order_by('-date')
        context['academic_year_list'] = AcademicYear.objects.all()
        context['current_academic_year'] = current_academic_year.id

        context['category_list'] = []
        for category in Category.objects.filter(post__teacher=self.object).distinct():
            context['category_list'].append({'category': category,
                                             'count': category.post_set.filter(teacher=self.object).count})
        return context


class DivisionPublicListView(generic.ListView):
    template_name = 'public/division/list.html'
    model = Division
    paginate_by = 12

    def get_queryset(self):
        division_list = Division.objects.all()
        today = datetime.date.today()
        academic_id = self.request.GET.get('academic_year')
        if academic_id:
            academic_year = AcademicYear.objects.filter(id=int(academic_id)).last()
        else:
            academic_year = AcademicYear.objects.filter(
                from_date__lte=today, to_date__gte=today).last()

        start_date = academic_year.from_date
        end_date = academic_year.to_date

        division_list = division_list.filter(
            Q(teacher__post__date__gte=start_date) & Q(teacher__post__date__lte=end_date) | Q(
                teacher__post__category__id=29)).distinct()
        division_list = division_list.annotate(
            total_coef=Sum('teacher__post__category__coef', filter=Q(teacher__post__status=2)),
            academ_ball=Sum('teacher__post__category__coef', filter=Q(
                teacher__post__category__group=Group.objects.get(id=3), teacher__post__status=2)),
            scien_ball=Sum('teacher__post__category__coef', filter=Q(
                teacher__post__category__group=Group.objects.get(id=2), teacher__post__status=2)),
            org_ball=Sum('teacher__post__category__coef', filter=Q(
                teacher__post__category__group=Group.objects.get(id=1), teacher__post__status=2)))

        if self.request.GET.get('name'):
            return division_list.filter(name__icontains=self.request.GET.get('name')).order_by('-total_coef')
        return division_list.order_by('-total_coef')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DivisionPublicListView, self).get_context_data(**kwargs)
        context['academic_year_list'] = AcademicYear.objects.all()
        today = datetime.date.today()
        current_academic_year = AcademicYear.objects.filter(
            from_date__lte=today, to_date__gte=today).last()
        context['current_academic_year'] = current_academic_year.id
        return context


class DivisionPublicDetailView(generic.DetailView):
    template_name = 'public/division/detail.html'
    model = Division

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(DivisionPublicDetailView, self).get_context_data(**kwargs)
        context['division_list'] = Division.objects.all()
        context['post_list'] = Post.objects.filter(teacher__division=self.object).order_by("-date")

        context['year_list'] = sorted(
            set(Post.objects.filter(teacher__in=self.object.teacher_set.all()).values_list("date__year", flat=True)))
        context['category_list'] = []
        for category in Category.objects.filter(post__teacher__division=self.object).distinct():
            context['category_list'].append({'category': category,
                                             'count': category.post_set.filter(
                                                 teacher__division=self.object).distinct().count()})
        return context


class ReviewerRequiredMixin(UserPassesTestMixin):
    """Restricts a view to DEPARTMENT_REVIEWER / SCIENTIFIC_DEPT_REVIEWER
    accounts (or superusers)."""

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.role in (
            User.Role.DEPARTMENT_REVIEWER, User.Role.SCIENTIFIC_DEPT_REVIEWER,
        )


class ReviewDashboardView(LoginRequiredMixin, ReviewerRequiredMixin, generic.TemplateView):
    """Lists submissions for an Inspector to approve or reject. Listing is
    server-rendered; the decision itself goes through
    api.v1.review.SubmissionDecisionView."""

    template_name = 'public/review/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        submissions = reviewer_visible_posts(self.request.user).select_related(
            'category', 'teacher', 'reviewed_by',
        ).order_by('-date')

        status_filter = self.request.GET.get('status', '1')
        if status_filter:
            submissions = submissions.filter(status=status_filter)
        if self.request.GET.get('academic_year'):
            submissions = submissions.filter(academic_years_id=self.request.GET['academic_year'])

        context['submissions'] = submissions
        context['status_filter'] = status_filter
        context['academic_year_list'] = AcademicYear.objects.all()
        context['pending_count'] = reviewer_visible_posts(self.request.user).filter(status=1).count()
        return context


class StyledPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', 'form-control')


class ForcedPasswordChangeView(LoginRequiredMixin, PasswordChangeView):
    """Where every admin-issued default password (see user.admin.TeacherAdmin)
    sends the teacher on next login, via ForcePasswordChangeMiddleware."""

    template_name = 'public/user/password_change.html'
    form_class = StyledPasswordChangeForm
    success_url = reverse_lazy('user_public:password_change_done')

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.request.user.must_change_password:
            self.request.user.must_change_password = False
            self.request.user.save(update_fields=['must_change_password'])
        return response


class ForcedPasswordChangeDoneView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'public/user/password_change_done.html'


class TeacherSubmissionForm(forms.ModelForm):
    file = forms.FileField(required=False, help_text="Tasdiqlovchi hujjat (ixtiyoriy).")

    class Meta:
        model = Post
        fields = ['category', 'title', 'date']
        # type="date" makes the browser render a real calendar picker and
        # always submit ISO format (YYYY-MM-DD), avoiding locale-dependent
        # text parsing that rejected e.g. "24.11.2026" as invalid.
        widgets = {'date': forms.DateInput(attrs={'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(is_delete=False)
        for name, field in self.fields.items():
            if name != 'file':
                field.widget.attrs.setdefault('class', 'form-control')


class TeacherRequiredMixin(UserPassesTestMixin):
    """Restricts a view to accounts with a linked Teacher profile."""

    def test_func(self):
        return getattr(self.request.user, 'teacher_profile', None) is not None


class TeacherSubmissionView(LoginRequiredMixin, TeacherRequiredMixin, generic.CreateView):
    """Minimal self-service page: a teacher submits a new result (goes into
    the pending queue for Inspector review) and sees their own submissions."""

    template_name = 'public/teacher/submissions.html'
    form_class = TeacherSubmissionForm
    success_url = reverse_lazy('user_public:teacher_submissions')

    def form_valid(self, form):
        form.instance.teacher = self.request.user.teacher_profile
        form.instance.author = self.request.user
        form.instance.body = form.instance.title
        form.instance.status = 1
        response = super().form_valid(form)
        uploaded_file = form.cleaned_data.get('file')
        if uploaded_file:
            Document.objects.create(post=self.object, file=uploaded_file, author=self.request.user)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['submissions'] = Post.objects.filter(
            teacher=self.request.user.teacher_profile,
        ).order_by('-date')
        return context
