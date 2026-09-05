# Seeds the three KPI domain Groups and the full official criteria matrix as
# Category rows, verified against "Оценка ППС" (25.10.2023) Sections 1-3.
#
# Distribution/co-author fields (WEIGHTED_SPLIT/FLAT_TEAM, max_co_authors,
# self_submittable) drive the faculty submission modal's Indicator Picker and
# its live score estimator; they carry no meaning for the pre-existing
# admin-authored Post flow, which ignores them.
from django.db import migrations

SOLO = 'SOLO'
FLAT_TEAM = 'FLAT_TEAM'
WEIGHTED_SPLIT = 'WEIGHTED_SPLIT'

GROUP_DISCIPLINE = 'Академическая'
GROUP_QUALIFICATION = 'Квалификация и организация'
GROUP_RESEARCH = 'Научная деятельность'

# (name, coef, group, distribution, max_co_authors, co_author_share_percent,
#  requires_doi, self_submittable, limit)
CATEGORIES = [
    # --- Section 1: Academic discipline ---------------------------------------
    ('Несоответствие требованиям заполненности Moodle', -5, GROUP_DISCIPLINE, SOLO, None, 50.0, False, False, None),
    ('Срыв занятия', -5, GROUP_DISCIPLINE, SOLO, None, 50.0, False, False, None),
    ('Опоздание на занятие', -3, GROUP_DISCIPLINE, SOLO, None, 50.0, False, False, None),
    ('Объяснительный', -5, GROUP_DISCIPLINE, SOLO, None, 50.0, False, False, None),
    ('Положительная рецензия комиссии по оценке качества преподавания',
     5, GROUP_DISCIPLINE, SOLO, None, 50.0, False, True, None),
    ('Негативная рецензия комиссии по оценке качества преподавания',
     -5, GROUP_DISCIPLINE, SOLO, None, 50.0, False, False, None),

    # --- Section 2: Qualification & organizational activity -------------------
    ('Coursera — Specialization', 40, GROUP_QUALIFICATION, SOLO, None, 50.0, False, True, None),
    ('Coursera — Advanced', 10, GROUP_QUALIFICATION, SOLO, None, 50.0, False, True, None),
    ('Coursera — Intermediate', 8, GROUP_QUALIFICATION, SOLO, None, 50.0, False, True, None),
    ('Квалификационный сертификат — специализация', 40, GROUP_QUALIFICATION, SOLO, None, 50.0, False, True, None),
    ('Квалификационный сертификат — свыше 40 часов', 10, GROUP_QUALIFICATION, SOLO, None, 50.0, False, True, None),
    ('Квалификационный сертификат — до 40 часов', 5, GROUP_QUALIFICATION, SOLO, None, 50.0, False, True, None),
    ('Конференция, форум (организация)', 20, GROUP_QUALIFICATION, FLAT_TEAM, 3, 100.0, False, True, None),
    ('Семинар / мастер-класс / учебная практика (организация)',
     5, GROUP_QUALIFICATION, FLAT_TEAM, 2, 100.0, False, True, None),
    ('Конкурс / выставка / ярмарка (организация)', 3, GROUP_QUALIFICATION, FLAT_TEAM, 1, 100.0, False, True, None),
    ('Другие организационные мероприятия', 2, GROUP_QUALIFICATION, FLAT_TEAM, 1, 100.0, False, True, None),

    # --- Section 3: Scientific research & IP -----------------------------------
    ('Международный проект (грант)', 150, GROUP_RESEARCH, WEIGHTED_SPLIT, 4, 50.0, False, True, None),
    ('Государственный проект — 1 категория (фундаментальный)',
     100, GROUP_RESEARCH, WEIGHTED_SPLIT, 3, 50.0, False, True, None),
    ('Государственный проект — 2 категория (прикладной/инновационный)',
     90, GROUP_RESEARCH, WEIGHTED_SPLIT, 3, 50.0, False, True, None),

    ('Руководство DSc (после защиты)', 55, GROUP_RESEARCH, SOLO, None, 50.0, False, True, None),
    ('Руководство PhD (после защиты)', 45, GROUP_RESEARCH, SOLO, None, 50.0, False, True, None),

    ('Руководство студентом — олимпиада', 55, GROUP_RESEARCH, SOLO, None, 50.0, False, True, None),
    ('Руководство студентом — президентская стипендия', 45, GROUP_RESEARCH, SOLO, None, 50.0, False, True, None),
    ('Руководство студентом — международный конкурс', 20, GROUP_RESEARCH, SOLO, None, 50.0, False, True, None),
    ('Руководство студентом — другие значимые конкурсы', 15, GROUP_RESEARCH, SOLO, None, 50.0, False, True, None),

    ('Защита DSc', 60, GROUP_RESEARCH, SOLO, None, 50.0, False, True, None),
    ('Защита PhD', 50, GROUP_RESEARCH, SOLO, None, 50.0, False, True, None),
    ('Академик', 80, GROUP_RESEARCH, SOLO, None, 50.0, False, True, None),
    ('Член Академии', 40, GROUP_RESEARCH, SOLO, None, 50.0, False, True, None),
    ('Профессор (звание)', 40, GROUP_RESEARCH, SOLO, None, 50.0, False, True, None),
    ('Доцент (звание)', 30, GROUP_RESEARCH, SOLO, None, 50.0, False, True, None),

    ('Патент на изобретение (международный)', 60, GROUP_RESEARCH, WEIGHTED_SPLIT, 2, 50.0, False, True, None),
    ('Патент на изобретение (республиканский)', 50, GROUP_RESEARCH, WEIGHTED_SPLIT, 2, 50.0, False, True, None),
    ('Патент на полезную модель', 20, GROUP_RESEARCH, WEIGHTED_SPLIT, 2, 50.0, False, True, None),
    ('Свидетельство о регистрации программы', 10, GROUP_RESEARCH, WEIGHTED_SPLIT, 2, 50.0, False, True, None),

    ('Scopus / Web of Science — Q1', 70, GROUP_RESEARCH, WEIGHTED_SPLIT, 2, 50.0, True, True, None),
    ('Scopus / Web of Science — Q2', 65, GROUP_RESEARCH, WEIGHTED_SPLIT, 2, 50.0, True, True, None),
    ('Scopus / Web of Science — Q3', 60, GROUP_RESEARCH, WEIGHTED_SPLIT, 2, 50.0, True, True, None),
    ('Scopus / Web of Science — Q4', 55, GROUP_RESEARCH, WEIGHTED_SPLIT, 2, 50.0, True, True, None),

    ('Публикация — журнал ВАК', 15, GROUP_RESEARCH, WEIGHTED_SPLIT, 1, 50.0, True, True, None),
    ('Публикация — международный журнал (список ВАК)', 20, GROUP_RESEARCH, WEIGHTED_SPLIT, 1, 50.0, True, True, None),
    ('Публикация — международный журнал', 15, GROUP_RESEARCH, WEIGHTED_SPLIT, 1, 50.0, True, True, None),
    ('Публикация — журнал YTIT', 15, GROUP_RESEARCH, WEIGHTED_SPLIT, 1, 50.0, True, True, None),
    ('Публикация — республиканский журнал', 5, GROUP_RESEARCH, WEIGHTED_SPLIT, 1, 50.0, True, True, None),

    ('Конференция, индексируемая в Scopus/WoS', 40, GROUP_RESEARCH, WEIGHTED_SPLIT, 1, 50.0, False, True, None),
    ('Международная конференция — с докладом', 12, GROUP_RESEARCH, WEIGHTED_SPLIT, 1, 50.0, False, True, None),
    ('Международная конференция — участие', 8, GROUP_RESEARCH, WEIGHTED_SPLIT, 1, 50.0, False, True, None),
    ('Республиканская конференция — с докладом', 8, GROUP_RESEARCH, WEIGHTED_SPLIT, 1, 50.0, False, True, None),
    ('Республиканская конференция — участие', 5, GROUP_RESEARCH, WEIGHTED_SPLIT, 1, 50.0, False, True, None),

    ('Учебник (гриф Министерства, действует 2 года)',
     40, GROUP_RESEARCH, WEIGHTED_SPLIT, 1, 50.0, False, True, None),
    ('Учебник (утверждён советом KIUT)', 30, GROUP_RESEARCH, WEIGHTED_SPLIT, 1, 50.0, False, True, None),
    ('Монография', 30, GROUP_RESEARCH, WEIGHTED_SPLIT, 1, 50.0, False, True, None),
    ('Учебное пособие (гриф)', 25, GROUP_RESEARCH, WEIGHTED_SPLIT, 1, 50.0, False, True, None),
    ('Методическое пособие (совет KIUT)', 20, GROUP_RESEARCH, WEIGHTED_SPLIT, 1, 50.0, False, True, None),
]


def seed_categories(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Category = apps.get_model('category', 'Category')
    User = apps.get_model('user', 'User')

    system_user = User.objects.filter(role='SYSTEM').first()
    if system_user is None:
        system_user = User.objects.filter(is_superuser=True).first()
    if system_user is None:
        system_user = User.objects.create(
            username='system', email='system@kiut.uz', role='SYSTEM', is_staff=False, is_active=True,
        )
        system_user.set_unusable_password()
        system_user.save()

    groups_by_name = {}
    for group_name in (GROUP_DISCIPLINE, GROUP_QUALIFICATION, GROUP_RESEARCH):
        group, _ = Group.objects.get_or_create(name=group_name)
        groups_by_name[group_name] = group

    for (name, coef, group_name, distribution, max_co_authors, share_pct,
         requires_doi, self_submittable, limit) in CATEGORIES:
        # Historical models from apps.get_model() bypass django-modeltranslation's
        # descriptors, so the per-language columns must be set explicitly here —
        # assigning only `name` would leave name_ru/name_uz/name_en blank.
        Category.objects.get_or_create(
            name_ru=name,
            group=groups_by_name[group_name],
            defaults={
                'name': name,
                'name_uz': name,
                'name_en': name,
                'coef': coef,
                'author': system_user,
                'distribution': distribution,
                'max_co_authors': max_co_authors,
                'co_author_share_percent': share_pct,
                'requires_doi': requires_doi,
                'self_submittable': self_submittable,
                'limit': limit,
            },
        )


def remove_categories(apps, schema_editor):
    Category = apps.get_model('category', 'Category')
    Group = apps.get_model('auth', 'Group')
    Category.objects.filter(name_ru__in=[c[0] for c in CATEGORIES]).delete()
    Group.objects.filter(name__in=[GROUP_DISCIPLINE, GROUP_QUALIFICATION, GROUP_RESEARCH]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('category', '0009_category_coauthorship_rules'),
        ('user', '0010_faculty_registration_and_otp'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(seed_categories, remove_categories),
    ]
