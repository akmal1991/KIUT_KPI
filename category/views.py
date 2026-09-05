from datetime import datetime
from django.core.cache import cache
from django.contrib.auth.models import Group
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from category.models import Category, get_permission_queryset, StatisticsScientific, CoefficientCategoryByYear
from post.models import AcademicYear


class CategoryAdminListView(LoginRequiredMixin, generic.ListView):
    template_name = 'administrator/category/list.html'
    model = Category
    queryset = Category.objects.all()
    paginate_by = 12

    def get_context_data(self, *, object_list=None, **kwargs):
        resp = super(CategoryAdminListView, self).get_context_data(**kwargs)
        resp['group_list'] = Group.objects.all()
        academic_years = AcademicYear.objects.all()

        if self.request.GET.get('limit_by_year'):
            academic_year_id = self.request.GET.get('limit_by_year')
        else:
            academic_year_id = AcademicYear.get_current_academic_year().id
        resp['limit_by_year'] = academic_year_id

        resp['academic_years_for_select'] = academic_years
        resp['academic_years'] = academic_years.order_by('-id')[:3]
        resp['academic_years'] = list(resp['academic_years'])[::-1]
        resp['category_limit_count'] = Category.get_categories_many_of_limit(academic_year_id).count()
        return resp

    def get_queryset(self):
        categories = get_permission_queryset(self.request.user).filter(is_delete=False)
        if self.request.GET.get('limit_by_year'):
            academic_year_id = int(self.request.GET.get('limit_by_year'))
            categories = Category.get_categories_many_of_limit(academic_year_id)

        if self.request.GET.get('group'):
            return categories.filter(group=self.request.GET.get('group'))
        if self.request.GET.get('name'):
            return categories.filter(name__icontains=self.request.GET.get('name'))
        return categories


class CategoryLimitExpired(LoginRequiredMixin, generic.DetailView):
    template_name = 'administrator/category/category-coefficient.html'
    model = Category

    def get_context_data(self, *, object_list=None, **kwargs):
        resp = super(CategoryLimitExpired, self).get_context_data(**kwargs)
        resp['academic_years'] = AcademicYear.objects.all()
        resp['category_coefficients'] = self.object.coefficientcategorybyyear_set.all()
        return resp


class CoefficientCategoryByYearAdminListView(LoginRequiredMixin, generic.DetailView):
    template_name = 'administrator/category/category-coefficient.html'
    model = Category

    def get_context_data(self, *, object_list=None, **kwargs):
        resp = super(CoefficientCategoryByYearAdminListView, self).get_context_data(**kwargs)
        resp['academic_years'] = AcademicYear.objects.all()
        resp['category_coefficients'] = self.object.coefficientcategorybyyear_set.all()
        return resp


class StatisticsScientificView(generic.ListView):
    template_name = 'public/post/static_scientific.html'
    model = StatisticsScientific

    def get_context_data(self, *, object_list=None, **kwargs):
        resp = super(StatisticsScientificView, self).get_context_data(**kwargs)
        status_teachers = []

        cache_key = 'status_teachers'
        cached_status_teachers = cache.get(cache_key)

        if cached_status_teachers:
            status_teachers = cached_status_teachers
        else:
            academic_years = AcademicYear.objects.all()[:4]
            for academic_year in academic_years:
                status = {
                    "year": f'{academic_year.years}',
                    "gt_150": academic_year.academicball.gt_150,
                    "lt_150": academic_year.academicball.lt_150,
                    "lt_100": academic_year.academicball.lt_100,
                    "lt_55": academic_year.academicball.lt_55
                }
                status_teachers.insert(0, status)

            cache.set(cache_key, status_teachers, timeout=60 * 60)

        resp['status_teachers'] = status_teachers
        return resp

    def get_queryset(self):
        return StatisticsScientific.objects.all()
