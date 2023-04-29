# Generated by Django 4.2 on 2023-04-29 06:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='preset',
            name='linked',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='schedule.preset'),
        ),
        migrations.AlterField(
            model_name='preset',
            name='intensity',
            field=models.PositiveIntegerField(choices=[(0, 'OFF'), (1, 'SLEEP'), (2, 'WORK'), (3, 'WORK+'), (4, 'bk-OVER'), (5, 'OVER')], default=0),
        ),
    ]