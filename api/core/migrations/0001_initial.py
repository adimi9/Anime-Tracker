# Generated by Django 5.1.6 on 2025-03-03 06:28

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='genres', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WatchStatus',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('status', models.CharField(choices=[('watching', 'Watching'), ('completed', 'Completed'), ('on_hold', 'On Hold'), ('dropped', 'Dropped'), ('plan_to_watch', 'Plan to Watch')], default='plan_to_watch', max_length=20)),
                ('progress', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='watch_statuses', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Anime',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('release_date', models.DateField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='animes', to=settings.AUTH_USER_MODEL)),
                ('genres', models.ManyToManyField(related_name='animes', to='core.genre')),
                ('watch_status', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='animes', to='core.watchstatus')),
            ],
        ),
    ]
