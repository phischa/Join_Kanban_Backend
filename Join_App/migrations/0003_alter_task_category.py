# Generated by Django 5.1.5 on 2025-03-27 17:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Join_App', '0002_alter_task_priority'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='category',
            field=models.CharField(choices=[('todo', 'To Do'), ('inprogress', 'In Progress'), ('awaitfeedback', 'Await Feedback'), ('done', 'Done')], default='todo', max_length=15),
        ),
    ]
