from celery import shared_task
from user.models import Teacher
from post.models import AcademicYear
from category.models import AcademicBall


@shared_task
def status_ball_teachers():
    academic_years = AcademicYear.objects.all()
    for academic_year in academic_years:
        gt_150 = 0
        lt_150 = 0
        lt_100 = 0
        lt_55 = 0

        for teacher in Teacher.objects.all():
            if teacher.status == 3 and teacher.ext_date is not None:
                if teacher.ext_date > academic_year.to_date:
                    ball = teacher.get_total_ball_by_year(academic_year.id)
                    if 55 > ball:
                        lt_55 += 1
                    elif 55 <= ball < 100:
                        lt_100 += 1
                    elif 100 <= ball < 150:
                        lt_150 += 1
                    elif ball >= 150:
                        gt_150 += 1

            else:
                ball = teacher.get_total_ball_by_year(academic_year.id)
                if 55 > ball:
                    lt_55 += 1
                elif 55 <= ball < 100:
                    lt_100 += 1
                elif 100 <= ball < 150:
                    lt_150 += 1
                elif ball >= 150:
                    gt_150 += 1

        if not AcademicBall.objects.filter(academic_year=academic_year):
            try:
                AcademicBall.objects.create(academic_year=academic_year).save()
            except:
                pass
        academic_year.academicball.gt_150 = gt_150
        academic_year.academicball.lt_150 = lt_150
        academic_year.academicball.lt_100 = lt_100
        academic_year.academicball.lt_55 = lt_55
        academic_year.academicball.save()
