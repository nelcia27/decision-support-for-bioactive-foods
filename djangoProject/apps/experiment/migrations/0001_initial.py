# Generated by Django 3.1.3 on 2020-12-12 17:03

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import re


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BasicIngredient',
            fields=[
                ('name', models.CharField(max_length=300, primary_key=True, serialize=False, unique=True)),
                ('percentage', models.PositiveIntegerField(default=10, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
            ],
        ),
        migrations.CreateModel(
            name='BasicIngredientBase',
            fields=[
                ('name', models.CharField(editable=False, max_length=300, primary_key=True, serialize=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('name', models.CharField(editable=False, max_length=300, primary_key=True, serialize=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='DetailedMetrics',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('numberOfRepeat', models.PositiveIntegerField(default=1)),
                ('numberOfSeries', models.PositiveIntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='ExternalFactor',
            fields=[
                ('name', models.CharField(editable=False, max_length=300, primary_key=True, serialize=False, unique=True)),
                ('numberOfValues', models.PositiveIntegerField(default=3)),
                ('unit', models.CharField(max_length=30)),
                ('values', models.CharField(max_length=150, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')])),
            ],
        ),
        migrations.CreateModel(
            name='Metrics',
            fields=[
                ('name', models.CharField(editable=False, max_length=300, primary_key=True, serialize=False, unique=True)),
                ('unit', models.CharField(max_length=30)),
                ('scale', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='SupplementBase',
            fields=[
                ('name', models.CharField(editable=False, max_length=300, primary_key=True, serialize=False, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Supplement',
            fields=[
                ('name', models.CharField(max_length=300, primary_key=True, serialize=False, unique=True)),
                ('percentage', models.PositiveIntegerField(default=10, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('basicIngredientBase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiment.basicingredientbase')),
                ('supplementBase', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiment.supplementbase')),
            ],
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('externalFactor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiment.externalfactor')),
                ('supplement', models.ManyToManyField(to='experiment.Supplement')),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('value', models.CharField(max_length=1500)),
                ('numberOfRepeat', models.PositiveIntegerField()),
                ('numberOfSeries', models.PositiveIntegerField()),
                ('detailedMetric', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiment.detailedmetrics')),
            ],
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('basicWeight', models.PositiveIntegerField(default=100)),
                ('ingredients', models.ManyToManyField(to='experiment.BasicIngredient')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('name', models.CharField(editable=False, max_length=300, primary_key=True, serialize=False, unique=True)),
                ('description', models.CharField(max_length=1500)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiment.category')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiment.recipe')),
            ],
        ),
        migrations.CreateModel(
            name='Experiment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=400)),
                ('description', models.CharField(max_length=1500)),
                ('link', models.CharField(max_length=600)),
                ('createDate', models.DateTimeField(auto_now_add=True)),
                ('numberOfMeasuredProperties', models.PositiveIntegerField(default=1)),
                ('publicView', models.BooleanField(default=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('detailedMetrics', models.ManyToManyField(to='experiment.DetailedMetrics')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiment.product')),
            ],
        ),
        migrations.AddField(
            model_name='detailedmetrics',
            name='metric',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiment.metrics'),
        ),
        migrations.AddField(
            model_name='detailedmetrics',
            name='sample',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiment.sample'),
        ),
        migrations.AddField(
            model_name='basicingredient',
            name='basicIngredientBase',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='experiment.basicingredientbase'),
        ),
    ]
