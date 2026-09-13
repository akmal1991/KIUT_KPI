from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0008_user_role_and_teacher_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='role',
            field=models.CharField(
                choices=[
                    ('FACULTY', 'Faculty'),
                    ('DEPARTMENT_REVIEWER', 'Department Reviewer'),
                    ('SCIENTIFIC_DEPT_REVIEWER', 'Scientific Department Reviewer'),
                    ('ADMIN', 'Administrator'),
                ],
                default='FACULTY', max_length=32,
            ),
        ),
    ]
