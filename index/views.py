import datetime
from django.core.cache import cache
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from user.models import Teacher
from post.models import Post, AcademicYear

from django.shortcuts import render


def public_handler404(request, exception, template_name="public/404.html"):
    context = {}
    response = render(request, "public/404.html", context)
    response.status_code = 404
    return response


def administrator_handler404(request, exception, template_name="administrator/404.html"):
    context = {}
    response = render(request, "administrator/404.html", context)
    response.status_code = 404
    return response


class IndexAdminView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'administrator/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexAdminView, self).get_context_data(**kwargs)
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
        context['month_list'] = month_list
        context['teacher_list'] = teachers[:40]
        context['current_academic_year'] = current_academic_year.id
        return context


class IndexPublicView(generic.TemplateView):
    template_name = 'public/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexPublicView, self).get_context_data(**kwargs)
        context['academic_year_list'] = AcademicYear.objects.all()
        today = datetime.date.today()
        month_list = []
        current_academic_year = AcademicYear.objects.filter(
            from_date__lte=today, to_date__gte=today).last()
        teachers = Teacher.objects.all()

        teachers_cache_key = f'teachers_{current_academic_year.id}'
        month_cache_key = f'month_list_{current_academic_year.id}'

        cached_teachers = cache.get(teachers_cache_key)
        if cached_teachers:
            teachers = cached_teachers
        else:
            if self.request.GET.get('academic_year'):
                cur_aca_year = self.request.GET.get('academic_year')
                teachers = sorted(teachers, key=lambda t: t.get_total_ball_by_year(int(cur_aca_year)), reverse=True)
                current_academic_year = AcademicYear.objects.filter(id=int(cur_aca_year)).last()
            else:
                teachers = sorted(teachers, key=lambda t: t.get_total_ball_by_year(current_academic_year.id),
                                  reverse=True)

            cache.set(teachers_cache_key, teachers[:40], timeout=60 * 60)

        cached_month_list = cache.get(month_cache_key)
        if cached_month_list:
            month_list = cached_month_list
        else:
            from_date = current_academic_year.from_date
            to_date = current_academic_year.to_date
            while from_date <= to_date:
                month_list.append(from_date.strftime("%b"))
                from_date += datetime.timedelta(days=31)
            month_list.append(month_list[0])

            cache.set(month_cache_key, month_list, timeout=60 * 15)

        context['month_list'] = month_list
        context['teacher_list'] = teachers[:40]
        context['post_list'] = Post.objects.order_by('-id')[:40]
        context['current_academic_year'] = current_academic_year.id
        return context
