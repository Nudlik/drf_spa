# Generated by Django 5.0.3 on 2024-03-13 16:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0002_alter_habit_link_habit_alter_habit_time_to_complete'),
    ]

    operations = [
        migrations.AlterField(
            model_name='habit',
            name='periodic',
            field=models.IntegerField(choices=[(0, 'Ежедневно'), (1, 'Понедельник'), (2, 'Вторник'), (3, 'Среда'), (4, 'Четверг'), (5, 'Пятница'), (6, 'Суббота'), (7, 'Воскресенье')], default=0, verbose_name='Периодичность'),
        ),
    ]
