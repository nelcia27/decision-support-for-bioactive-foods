from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, validate_comma_separated_integer_list


class Category(models.Model):
    name = models.CharField(primary_key=True, max_length=300, unique=True)

    def __str__(self):
        return self.name


class BasicIngredientBase(models.Model):
    name = models.CharField(primary_key=True, max_length=300, unique=True)

    def __str__(self):
        return self.name


class BasicIngredient(models.Model):
    name = models.CharField(primary_key=True, max_length=300, unique=True)
    percentage = models.PositiveIntegerField(default=10,
                                             blank=False,
                                             validators=[MinValueValidator(0), MaxValueValidator(100)])
    basicIngredientBase = models.ForeignKey(BasicIngredientBase, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    basicWeight = models.PositiveIntegerField(default=100, blank=False)
    ingredients = models.ManyToManyField(BasicIngredient)

    def __str__(self):
        return self.id


class Product(models.Model):
    name = models.CharField(primary_key=True, max_length=300, unique=True, editable=False)
    description = models.CharField(max_length=1500)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class SupplementBase(models.Model):
    name = models.CharField(primary_key=True, max_length=300, unique=True)

    def __str__(self):
        return self.name


class Supplement(models.Model):
    name = models.CharField(primary_key=True, max_length=300, unique=True)
    percentage = models.PositiveIntegerField(default=10,
                                             blank=False,
                                             validators=[MinValueValidator(0), MaxValueValidator(100)])
    basicIngredientBase = models.ForeignKey(BasicIngredientBase, on_delete=models.CASCADE)
    supplementBase = models.ForeignKey(SupplementBase, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class ExternalFactor(models.Model):
    name = models.CharField(primary_key=True, max_length=300, unique=True)
    numberOfValues = models.PositiveIntegerField(default=3, blank=False)
    unit = models.CharField(max_length=30)
    values = models.CharField(validators=[validate_comma_separated_integer_list], max_length=150)

    def __str__(self):
        return self.name


class Sample(models.Model):
    id = models.AutoField(primary_key=True)
    externalFactor = models.ForeignKey(ExternalFactor, on_delete=models.CASCADE)
    supplement = models.ManyToManyField(Supplement)

    def __str__(self):
        return self.name


class Metrics(models.Model):
    name = models.CharField(primary_key=True, max_length=300, unique=True)
    unit = models.CharField(max_length=30)
    scale = models.CharField(max_length=30)

    def __str__(self):
        return self.name


class DetailedMetrics(models.Model):
    id = models.AutoField(primary_key=True)
    numberOfRepeat = models.PositiveIntegerField(default=1, blank=False)
    numberOfSeries = models.PositiveIntegerField(default=1, blank=False)
    metric = models.ForeignKey(Metrics, on_delete=models.CASCADE)
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE)

    def __str__(self):
        return self.id


class Result(models.Model):
    id = models.AutoField(primary_key=True)
    value = models.CharField(blank=False, max_length=1500)
    numberOfRepeat = models.PositiveIntegerField(blank=False)
    numberOfSeries = models.PositiveIntegerField(blank=False)
    detailedMetric = models.ForeignKey(DetailedMetrics, on_delete=models.CASCADE)

    def __str__(self):
        return self.id


class Experiment(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=400)
    description = models.CharField(max_length=1500)
    link = models.CharField(max_length=600)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    createDate = models.DateTimeField(auto_now_add=True)
    numberOfMeasuredProperties = models.PositiveIntegerField(default=1, blank=False)
    publicView = models.BooleanField(default=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    detailedMetrics = models.ManyToManyField(DetailedMetrics)

    def __str__(self):
        return self.name




