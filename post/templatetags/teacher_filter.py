from django import template

register = template.Library()


@register.simple_tag()
def get_total_ball_by_year(teacher, year):
    return teacher.get_total_ball_by_year(int(year))
