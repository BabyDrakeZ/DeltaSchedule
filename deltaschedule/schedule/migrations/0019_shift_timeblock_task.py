# Generated by Django 4.2 on 2023-05-21 13:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0018_remove_task_preset_remove_task_schedule_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('context', models.CharField(blank=True, default='', max_length=255)),
                ('linked', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='schedule.shift')),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shifts', to='schedule.schedule')),
                ('work_key', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schedule.workkey')),
            ],
        ),
        migrations.CreateModel(
            name='TimeBlock',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('days', models.SmallIntegerField(default=0, help_text='(autofills 1 if start > end)', verbose_name='Stetched Days')),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('Shift', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='blocks', to='schedule.shift')),
            ],
            options={
                'ordering': ['order', 'start_time'],
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('week_number', models.CharField(blank=True, max_length=2)),
                ('start_date', models.DateField()),
                ('context', models.CharField(blank=True, default='', max_length=255)),
                ('color', models.CharField(blank=True, default='#FFFFFF', max_length=7)),
                ('preset', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='schedule.shift')),
                ('schedule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tasks', to='schedule.schedule')),
                ('timeblock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='schedule.timeblock')),
                ('work_key', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedule.workkey')),
            ],
        ),
    ]
