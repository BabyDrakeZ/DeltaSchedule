# Generated by Django 4.2 on 2023-05-21 13:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0017_alter_task_color_alter_workkey_color'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='preset',
        ),
        migrations.RemoveField(
            model_name='task',
            name='schedule',
        ),
        migrations.RemoveField(
            model_name='task',
            name='timeblock',
        ),
        migrations.RemoveField(
            model_name='task',
            name='work_key',
        ),
        migrations.RemoveField(
            model_name='timeblock',
            name='Shift',
        ),
        migrations.DeleteModel(
            name='Shift',
        ),
        migrations.DeleteModel(
            name='Task',
        ),
        migrations.DeleteModel(
            name='TimeBlock',
        ),
    ]