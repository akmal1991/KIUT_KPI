import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
# Create your views here.
from category.models import get_permission_queryset
from post.models import Post, AcademicYear
from user.models import Teacher, Target
from django.db.models import Q
from django.contrib.auth.models import Group


class PostListAdminView(LoginRequiredMixin, generic.ListView):
    model = Post
    # queryset = Post.objects.all()
    paginate_by = 15
    template_name = 'administrator/post/list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostListAdminView, self).get_context_data(**kwargs)
        context['category_list'] = get_permission_queryset(self.request.user).filter(is_delete=False)
        context['teacher_list'] = Teacher.objects.all()
        context['academic_years'] = AcademicYear.objects.all()
        context['current_academic_year'] = AcademicYear.get_current_academic_year()
        context['group_list'] = self.request.user.groups.all()
        return context

    def get_queryset(self):

        posts = Post.objects.filter(category__in=get_permission_queryset(self.request.user))
        if self.request.GET.get('category'):
            posts = posts.filter(category=self.request.GET.get('category'))

        if self.request.GET.get('name'):
            name = self.request.GET.get('name')
            posts = posts.filter(
                Q(title__icontains=name) |
                Q(title_ru__icontains=name) |
                Q(title_en__icontains=name) |
                Q(title_uz__icontains=name) |
                Q(teacher__first_name__icontains=name) |
                Q(teacher__last_name__icontains=name) |
                Q(teacher__father_name__icontains=name)
            )

        if self.request.GET.get('select-data'):
            if self.request.GET.get('select-data') == 'date-publications-desc':
                posts = Post.objects.all().order_by('-date')
            elif self.request.GET.get('select-data') == 'date-publications-asc':
                posts = Post.objects.all().order_by('date')
            elif self.request.GET.get('select-data') == 'date-created-desc':
                posts = Post.objects.all().order_by('-created')
            elif self.request.GET.get('select-data') == 'date-created-asc':
                posts = Post.objects.all().order_by('created')

        if self.request.GET.get('academic_year'):
            academic_year = self.request.GET.get('academic_year')
            posts = posts.filter(academic_years__id=academic_year)

        if self.request.GET.get('group'):
            group = self.request.GET.get('group')
            posts = posts.filter(category__group__id=group)

        if self.request.GET.get('teacher'):
            teacher = self.request.GET.get('teacher')
            posts = posts.filter(teacher__id=teacher)

        return posts


class PostCreateAdminView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'administrator/post/create.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostCreateAdminView, self).get_context_data(**kwargs)
        context['teacher_list'] = Teacher.objects.all()
        context['group_list'] = self.request.user.groups.all()
        context['category_list'] = get_permission_queryset(self.request.user).filter(is_delete=False)
        context['target_list'] = Target.objects.all()

        return context


class PostUpdateAdminView(LoginRequiredMixin, generic.DetailView):
    template_name = 'administrator/post/update.html'
    model = Post

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(PostUpdateAdminView, self).get_context_data(**kwargs)
        context['teacher_list'] = Teacher.objects.all()
        context['group_list'] = self.request.user.groups.all()
        context['category_list'] = get_permission_queryset(self.request.user).filter(is_delete=False)
        context['academic_years'] = AcademicYear.objects.all()
        context['target_list'] = Target.objects.all()
        return context


class PostListPublicView(generic.ListView):
    template_name = 'public/post/list.html'
    model = Post
    paginate_by = 12

    def get_queryset(self):
        posts = Post.objects.all()
        group_id = self.request.GET.get('group')
        if group_id:
            try:
                return Post.objects.filter(category__group_id=group_id)
            except:
                pass

        if self.request.GET.get('select-data'):
            if self.request.GET.get('select-data') == 'date-publications-desc':
                posts = Post.objects.all().order_by('-date')
            elif self.request.GET.get('select-data') == 'date-publications-asc':
                posts = Post.objects.all().order_by('date')
            elif self.request.GET.get('select-data') == 'date-created-desc':
                posts = Post.objects.all().order_by('-created')
            elif self.request.GET.get('select-data') == 'date-created-asc':
                posts = Post.objects.all().order_by('created')

        return posts


class PostDetailPublicView(generic.DetailView):
    template_name = 'public/post/detail.html'
    model = Post


class ReportingView(generic.TemplateView):
    template_name = 'administrator/post/reporting.html'

    def get_context_data(self, **kwargs):
        context = super(ReportingView, self).get_context_data(**kwargs)
        context['academic_year_list'] = AcademicYear.objects.all()
        today = datetime.date.today()
        month_list = []
        current_academic_year = AcademicYear.objects.filter(
            from_date__lte=today, to_date__gte=today).last()
        teachers = Teacher.objects.all()
        if self.request.GET.get('academic_year'):
            cur_aca_year = self.request.GET.get('academic_year')
            teachers = sorted(teachers, key=lambda t: t.get_total_ball_by_year(int(cur_aca_year)), reverse=True)
            current_academic_year = AcademicYear.objects.filter(id=int(cur_aca_year)).last()
            from_date = current_academic_year.from_date
            to_date = current_academic_year.to_date
            while from_date <= to_date:
                month_list.append(from_date.strftime("%b"))
                from_date += datetime.timedelta(days=31)

        else:

            from_date = current_academic_year.from_date
            to_date = current_academic_year.to_date
            while from_date <= to_date:
                month_list.append(from_date.strftime("%b"))
                from_date += datetime.timedelta(days=31)

            teachers = sorted(teachers, key=lambda t: t.get_total_ball_by_year(current_academic_year.id),
                              reverse=True)
        month_list.append(month_list[0])
        context['month_list'] = month_list
        context['teacher_list'] = teachers[:40]
        context['post_list'] = Post.objects.order_by('-id')[:40]
        context['current_academic_year'] = current_academic_year.id
        return context
