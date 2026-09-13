import os
import xlsxwriter
from django.conf import settings
from category.models import Category
from user.models import Teacher
from django.db.models import Sum, Q, FloatField, F, When, Case, IntegerField
from django.db.models.functions import Coalesce
from django.contrib.auth.models import Group


def excel_writer(academic_years):
    column = ['B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
              'W', 'X', 'Y', 'Z',
              'AA', 'AB', 'AC', 'AD', 'AE', 'AF', 'AG', 'AH', 'AI', 'AJ', 'AK', 'AL', 'AM', 'AN', 'AO', 'AP', 'AQ',
              'AR', 'AS', 'AT', 'AU', 'AV', 'AW', 'AX', 'AY', 'AZ']

    # Create a new Excel file and add a worksheet.
    workbook = xlsxwriter.Workbook(os.path.join(settings.MEDIA_ROOT, 'analysis.xlsx'))
    worksheet = workbook.add_worksheet('analysis')

    # 1 main column row
    merge_format = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'border': 1,
        'valign': 'vcenter',
        'text_wrap': True,
        'bg_color': '#dbd9d9'
    })

    text_format = workbook.add_format({

        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True
    })

    worksheet.set_column('A1:A1', 40)
    worksheet.set_row(1, 20)
    worksheet.write('A1', ' ', merge_format)

    worksheet.set_column('A2:A2', 40)
    worksheet.set_row(1, 20)
    main = 'Наименование'
    worksheet.write('A2', main, merge_format)

    i = 0
    for academic_year in academic_years:
        worksheet.set_column(f'{column[i]}1:{column[i + 1]}1', 20)
        worksheet.set_row(1, 20)
        main1 = f'{academic_year.years}'
        worksheet.merge_range(f'{column[i]}1:{column[i + 1]}1', main1, merge_format)

        worksheet.set_column(f'{column[i]}2:{column[i]}2', 10)
        main2 = 'Кол-во '
        worksheet.write(f'{column[i]}2', main2, merge_format)

        worksheet.set_column(f'{column[i + 1]}2:{column[i + 1]}2', 10)
        main3 = 'Баллы'
        worksheet.write(f'{column[i + 1]}2', main3, merge_format)

        i += 2

    c = 3
    for category in Category.objects.all():
        worksheet.set_column(f'A{c}:A{c}', 40)
        worksheet.set_row(1, 20)
        main = category.name
        worksheet.write(f'A{c}', main, merge_format)

        i = 0
        for academic_year in academic_years:
            post_count = category.post_set.filter(academic_years=academic_year, status=2).distinct().count()
            total_sum = round(category.get_coef(academic_year) * post_count, 2)

            worksheet.set_column(f'{column[i]}{c}:{column[i]}{c}', 10)
            worksheet.write(f'{column[i]}{c}', post_count, text_format)

            worksheet.set_column(f'{column[i + 1]}{c}:{column[i + 1]}{c}', 10)
            worksheet.write(f'{column[i + 1]}{c}', total_sum, text_format)

            i += 2

        c += 1

    workbook.close()
    return workbook


def excel_teachers(academic_year, division, name, uuid, level, order_by):
    years = academic_year.years

    # Создание нового Excel файла и добавление рабочего листа.
    workbook = xlsxwriter.Workbook(os.path.join(settings.MEDIA_ROOT, f'analysis_teachers_{years}.xlsx'))
    worksheet = workbook.add_worksheet('analysis')

    # Форматы для ячеек
    merge_format = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'border': 1,
        'valign': 'vcenter',
        'text_wrap': True,
        'bg_color': '#dbd9d9'
    })

    text_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True
    })

    # Настройка столбцов и строк
    worksheet.set_column(f'A1:H1', 100)
    worksheet.set_row(1, 20)
    worksheet.merge_range(f'A1:H1', str(years), merge_format)

    worksheet.set_column(f'A2:A2', 4)
    worksheet.write(f'A2', "#", merge_format)

    worksheet.set_column(f'B2:B2', 10)
    worksheet.write(f'B2', "ID", merge_format)

    worksheet.set_column('C2:C2', 40)
    worksheet.write('C2', 'Ф.И.О', merge_format)

    worksheet.set_column('D2:D2', 25)
    worksheet.write('D2', 'Кафедра', merge_format)

    worksheet.set_column('E2:E2', 15)
    worksheet.write('E2', 'Статус', merge_format)

    worksheet.set_column('F2:F2', 15)
    worksheet.write('F2', 'Дата регистрации', merge_format)

    worksheet.set_column('G2:G2', 5)
    worksheet.write('G2', 'Кол-во', merge_format)

    worksheet.set_column('H2:H2', 10)
    worksheet.write('H2', 'Баллы', merge_format)

    teachers = Teacher.objects.annotate(
        total_ball=Coalesce(
            Sum(
                Case(
                    # When a CoefficientCategoryByYear exists for the given academic year, use its coef
                    When(
                        post__category__coefficientcategorybyyear__academic_year=academic_year,
                        then=F('post__category__coefficientcategorybyyear__coef')
                    ),
                    # If no matching CoefficientCategoryByYear, use coef from Category
                    default=F('post__category__coef'),
                    output_field=FloatField()
                ),
                filter=(Q(post__academic_years=academic_year) | Q(post__category__id=29)) & Q(post__status=2)
            ),
            0,  # Default value if no coefficient is found
            output_field=FloatField()
        )
    ).order_by("total_ball").exclude(status=3)

    if division:
        teachers = teachers.filter(division=division)
    if uuid:
        teachers = teachers.filter(uuid=uuid)
    if level:
        teachers = teachers.filter(level=level)
    if name:
        teachers = teachers.filter(
            Q(first_name__icontains=name) |
            Q(last_name__icontains=name) |
            Q(father_name__contains=name)
        )
    if order_by == 'ball_asc':
        teachers = teachers.order_by('total_ball')
    if order_by == 'ball_desc':
        teachers = teachers.order_by('-total_ball')
    else:
        teachers = teachers.order_by('-total_ball', 'last_name', 'first_name', 'father_name')

    c = 3
    for teacher in teachers.distinct():
        post_count = teacher.post_set.filter(
            (Q(academic_years=academic_year) | Q(category__id=29)) & Q(status=2)
        ).distinct().count()
        worksheet.write(f'A{c}', c - 2, text_format)
        worksheet.write(f'B{c}', f'{teacher.uuid}', text_format)
        worksheet.write(f'C{c}', f'{teacher.get_full_name()}', text_format)
        worksheet.write(f'D{c}', f'{teacher.division.name if teacher.division else ""}', text_format)
        worksheet.write(f'E{c}', f'{teacher.get_status_display()}', text_format)
        worksheet.write(f'F{c}', f'{teacher.created.date()}', text_format)
        worksheet.write(f'G{c}', f'{post_count}', text_format)
        worksheet.write(f'H{c}', f'{teacher.get_total_ball_by_year(academic_id=academic_year.id)}', text_format)

        c += 1

    workbook.close()
    return workbook


def excel_teachers_form2(academic_year, division, name, uuid, level, order_by):
    years = academic_year.years

    # Создание нового Excel файла и добавление рабочего листа.
    workbook = xlsxwriter.Workbook(os.path.join(settings.MEDIA_ROOT, f'analysis_teachers_{years}.xlsx'))
    worksheet = workbook.add_worksheet('analysis')

    # Форматы для ячеек
    merge_format = workbook.add_format({
        'bold': 1,
        'align': 'center',
        'border': 1,
        'valign': 'vcenter',
        'text_wrap': True,
        'bg_color': '#dbd9d9'
    })

    text_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'text_wrap': True
    })

    # Настройка столбцов и строк
    worksheet.set_column(f'A1:I1', 100)
    worksheet.set_row(1, 20)
    worksheet.merge_range(f'A1:I1', str(years), merge_format)

    worksheet.set_column(f'A2:A2', 4)
    worksheet.write(f'A2', "#", merge_format)

    worksheet.set_column(f'B2:B2', 10)
    worksheet.write(f'B2', "ID", merge_format)

    worksheet.set_column('C2:C2', 40)
    worksheet.write('C2', 'Ф.И.О', merge_format)

    worksheet.set_column('D2:D2', 25)
    worksheet.write('D2', 'Кафедра', merge_format)

    worksheet.set_column('E2:E2', 15)
    worksheet.write('E2', 'Академический', merge_format)

    worksheet.set_column('F2:F2', 15)
    worksheet.write('F2', 'Квалификация и организация', merge_format)

    worksheet.set_column('G2:G2', 15)
    worksheet.write('G2', 'Научная деятельность', merge_format)

    worksheet.set_column('H2:H2', 5)
    worksheet.write('H2', 'Кол-во', merge_format)

    worksheet.set_column('I2:I2', 10)
    worksheet.write('I2', 'Баллы', merge_format)

    teachers = Teacher.objects.annotate(
        total_ball=Coalesce(
            Sum(
                Case(
                    # When a CoefficientCategoryByYear exists for the given academic year, use its coef
                    When(
                        post__category__coefficientcategorybyyear__academic_year=academic_year,
                        then=F('post__category__coefficientcategorybyyear__coef')
                    ),
                    # If no matching CoefficientCategoryByYear, use coef from Category
                    default=F('post__category__coef'),
                    output_field=FloatField()
                ),
                filter=(Q(post__academic_years=academic_year) | Q(post__category__id=29)) & Q(post__status=2)
            ),
            0,  # Default value if no coefficient is found
            output_field=FloatField()
        )
    ).order_by("-total_ball").exclude(status=3)

    if division:
        teachers = teachers.filter(division=division)
    if uuid:
        teachers = teachers.filter(uuid=uuid)
    if level:
        teachers = teachers.filter(level=level)
    if name:
        teachers = teachers.filter(
            Q(first_name__icontains=name) |
            Q(last_name__icontains=name) |
            Q(father_name__contains=name)
        )
    if order_by == 'ball_asc':
        teachers = teachers.order_by('total_ball')
    if order_by == 'ball_desc':
        teachers = teachers.order_by('-total_ball')
    else:
        teachers = teachers.order_by('-total_ball', 'last_name', 'first_name', 'father_name')

    c = 3
    for teacher in teachers.distinct():
        post_count = teacher.post_set.filter(
            (Q(academic_years=academic_year) | Q(category__id=29)) & Q(status=2)
        ).distinct().count()
        worksheet.write(f'A{c}', c - 2, text_format)
        worksheet.write(f'B{c}', f'{teacher.uuid}', text_format)
        worksheet.write(f'C{c}', f'{teacher.get_full_name()}', text_format)
        worksheet.write(f'D{c}', f'{teacher.division.name if teacher.division else ""}', text_format)

        worksheet.write(f'E{c}', f'{teacher.get_total_ball_by_group(3, academic_id=academic_year.id)}', text_format)
        worksheet.write(f'F{c}', f'{teacher.get_total_ball_by_group(1, academic_id=academic_year.id)}', text_format)
        worksheet.write(f'G{c}', f'{teacher.get_total_ball_by_group(2, academic_id=academic_year.id)}', text_format)

        worksheet.write(f'H{c}', f'{post_count}', text_format)
        worksheet.write(f'I{c}', f'{teacher.get_total_ball_by_year(academic_id=academic_year.id)}', text_format)

        c += 1

    workbook.close()
    return workbook
