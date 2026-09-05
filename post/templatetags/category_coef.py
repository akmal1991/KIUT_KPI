from django import template

register = template.Library()


@register.filter(name='get_coef_for_year')
def get_coef_for_year(category, academic_year):
    return category.get_coef(academic_year)


@register.filter(name='get_category_limit_by_year')
def get_category_limit_by_year(teacher, post):
    category = post.category
    academic_year = post.academic_years
    return teacher.get_limit_category(category, academic_year)
