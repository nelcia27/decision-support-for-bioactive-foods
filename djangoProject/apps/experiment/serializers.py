from rest_framework import serializers
from .models import *


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class BasicIngredientBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicIngredientBase
        fields = '__all__'


class BasicIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = BasicIngredient
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class SupplementBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplementBase
        fields = '__all__'


class SupplementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplement
        fields = '__all__'


class ExternalFactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExternalFactor
        fields = '__all__'


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = '__all__'


class DetailedMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetailedMetrics
        fields = '__all__'


class MetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Metrics
        fields = '__all__'


class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment
        fields = '__all__'


class ResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Result
        fields = '__all__'