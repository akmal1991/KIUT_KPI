import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('post', '0009_post_target'),
        ('user', '0008_user_role_and_teacher_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='status',
            field=models.IntegerField(
                choices=[(1, 'На рассмотрении'), (2, 'Одобрено'), (3, 'Отклонено')], default=1,
            ),
        ),
        migrations.AddField(
            model_name='post',
            name='review_comment',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='reviewed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='post',
            name='reviewed_by',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name='reviewed_posts', to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
