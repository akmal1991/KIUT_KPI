from django.db import migrations, models
import django.db.models.deletion


def add_default_academic_levels(apps, schema_editor):
    AcademicLevel = apps.get_model('user', 'AcademicLevel')
    AcademicLevel.objects.get_or_create(name='Доцент', name_ru='Доцент', name_en='Docent', name_uz='Dotsent')
    AcademicLevel.objects.get_or_create(name='Профессор', name_ru='Профессор', name_en='Professor', name_uz='Professor')


class Migration(migrations.Migration):
    dependencies = [
        ('user', '0005_alter_teacher_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicLevel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('name_ru', models.CharField(max_length=255, null=True)),
                ('name_en', models.CharField(max_length=255, null=True)),
                ('name_uz', models.CharField(max_length=255, null=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='teacher',
            name='academic_title',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                    to='user.academiclevel'),
        ),
        migrations.RunPython(add_default_academic_levels),  # Добавляем вызов функции при применении миграции
    ]
